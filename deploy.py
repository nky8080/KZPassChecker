"""デプロイ用スクリプト"""
import subprocess
import sys
import os
import json

def run_command(command, description, capture_output=True):
    """コマンドを実行"""
    print(f"\n{description}...")
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ {description} 完了")
            return result.stdout
        else:
            # ページャーを無効化してリアルタイム出力
            env = os.environ.copy()
            env['AWS_PAGER'] = ''
            result = subprocess.run(command, shell=True, check=True, env=env)
            print(f"✅ {description} 完了")
            return "success"
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e}")
        if capture_output and e.stderr:
            print(f"エラー出力: {e.stderr}")
        return None

def check_prerequisites():
    """前提条件の確認"""
    print("🔍 前提条件の確認")
    
    # AWS CLI確認
    aws_version = run_command("aws --version", "AWS CLI確認")
    if not aws_version:
        print("❌ AWS CLIがインストールされていません")
        return False
    
    # リージョン確認
    region = run_command("aws configure get region", "リージョン確認")
    if not region or "us-west-2" not in region:
        print("⚠️  リージョンをus-west-2に設定してください:")
        print("aws configure set region us-west-2")
        return False
    
    # 認証確認
    identity = run_command("aws sts get-caller-identity", "AWS認証確認")
    if not identity:
        print("❌ AWS認証が設定されていません")
        return False
    
    print("✅ 前提条件OK")
    return True

def configure_agentcore():
    """AgentCore設定"""
    print("\n🔧 AgentCore設定")
    
    # 既存設定確認
    if os.path.exists('.bedrock_agentcore.yaml'):
        print("既存の設定ファイルが見つかりました")
        response = input("再設定しますか？ (y/N): ")
        if response.lower() != 'y':
            return True
    
    # 設定実行（インタラクティブ）
    print("AgentCore設定を開始します...")
    print("プロンプトが表示されたら以下のように回答してください:")
    print("- Execution Role: Enterで自動作成")
    print("- ECR Repository: Enterで自動作成") 
    print("- OAuth Configuration: no")
    print("- Request Header Allowlist: no")
    print("- Long-term memory extraction: yes")
    
    try:
        subprocess.run("agentcore configure -e agent.py", shell=True, check=True)
        print("✅ AgentCore設定完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ AgentCore設定失敗: {e}")
        return False

def deploy_agentcore():
    """AgentCoreデプロイ"""
    print("\n🚀 AgentCoreデプロイ")
    
    try:
        # ページャーを無効化してデプロイ
        env = os.environ.copy()
        env['AWS_PAGER'] = ''
        
        result = subprocess.run("agentcore launch", shell=True, check=True, env=env)
        print("✅ デプロイ完了")
        
        # ステータス確認
        print("\n📊 デプロイ状況確認:")
        subprocess.run("agentcore status", shell=True, env=env)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ デプロイ失敗: {e}")
        return False

def test_deployment():
    """デプロイテスト"""
    print("\n🧪 デプロイテスト")
    
    try:
        env = os.environ.copy()
        env['AWS_PAGER'] = ''
        
        print("エージェント接続テスト...")
        # シンプルなテストで接続確認のみ
        result = subprocess.run(
            ['agentcore', 'invoke', '{"prompt": "こんにちは"}'], 
            check=True, capture_output=True, text=True, env=env, timeout=30
        )
        print("✅ エージェント接続テスト成功")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ テスト失敗: タイムアウト")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ テスト失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ テスト失敗: 予期しないエラー - {e}")
        return False

def main():
    print("🚀 文化の森お出かけパス エージェント デプロイ")
    
    # 前提条件確認
    if not check_prerequisites():
        print("\n❌ 前提条件を満たしていません")
        return
    
    # AgentCore設定
    if not configure_agentcore():
        print("\n❌ 設定に失敗しました")
        return
    
    # デプロイ実行
    if not deploy_agentcore():
        print("\n❌ デプロイに失敗しました")
        return
    
    # テスト実行
    if test_deployment():
        print("\n🎉 デプロイ完了！")
        print("\n📋 次のステップ:")
        print("1. agentcore status でステータス確認")
        print("2. agentcore invoke '{\"prompt\": \"明日の全施設の休館情報を教えて\"}' でテスト")
        print("3. CloudWatch ダッシュボードで監視")
        print("4. agentcore destroy で削除（必要に応じて）")
    else:
        print("\n⚠️  デプロイは完了しましたが、テストで問題が発生しました")

if __name__ == "__main__":
    main()