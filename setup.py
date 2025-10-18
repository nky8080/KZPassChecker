"""セットアップスクリプト"""
import subprocess
import sys
import os

def run_command(command, description):
    """コマンドを実行"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完了")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e}")
        print(f"エラー出力: {e.stderr}")
        return None

def main():
    print("🚀 文化の森お出かけパス 施設休館情報エージェント セットアップ")
    
    # 仮想環境の確認
    if not os.path.exists('.venv'):
        print("\n仮想環境を作成中...")
        run_command("python -m venv .venv", "仮想環境作成")
    
    # 仮想環境のアクティベート確認
    venv_python = ".venv\\Scripts\\python.exe" if os.name == 'nt' else ".venv/bin/python"
    if not os.path.exists(venv_python):
        print("❌ 仮想環境が正しく作成されていません")
        return
    
    # 依存関係のインストール
    install_cmd = f"{venv_python} -m pip install -r requirements.txt"
    run_command(install_cmd, "依存関係インストール")
    
    # AWS CLI設定確認
    print("\n🔧 AWS設定確認...")
    aws_check = run_command("aws configure get region", "AWS リージョン確認")
    if aws_check and "us-west-2" not in aws_check:
        print("⚠️  リージョンがus-west-2に設定されていません")
        print("以下のコマンドでリージョンを設定してください:")
        print("aws configure set region us-west-2")
    
    # Bedrock モデルアクセス確認の案内
    print("\n📋 次のステップ:")
    print("1. AWS CLIでus-west-2リージョンを設定")
    print("2. AWS Console → Bedrock → Model access → Claude 3.7 Sonnet を有効化")
    print("3. 仮想環境をアクティベート:")
    if os.name == 'nt':
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("4. ローカルテスト: python agent.py")
    print("5. AgentCore設定: agentcore configure -e agent.py")
    print("6. デプロイ: agentcore launch")

if __name__ == "__main__":
    main()