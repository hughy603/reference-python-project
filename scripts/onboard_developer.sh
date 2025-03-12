#!/bin/bash
set -e

echo "===== Enterprise Developer Onboarding ====="
echo "This script will set up your development environment with standardized tools and configurations."

# Check if running with appropriate permissions
if [ "$(id -u)" -eq 0 ]; then
    echo "ERROR: This script should not be run as root. Please run without sudo."
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Setup colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Tool versions
TERRAFORM_VERSION="1.5.7"
PYTHON_VERSION="3.11"
NODE_VERSION="18"
AWS_CLI_VERSION="2"

echo -e "\n${GREEN}Configuring Git with enterprise standards...${NC}"
# Configure Git
git config --global pull.rebase true
git config --global core.autocrlf input
git config --global core.fileMode false
git config --global init.defaultBranch main

if [ ! -f ~/.gitignore_global ]; then
    cat > ~/.gitignore_global << EOL
*~
.DS_Store
.idea/
.vscode/
*.sublime-*
.env
.env.*
!.env.template
*.log
node_modules/
__pycache__/
.pytest_cache/
.coverage
EOL
    git config --global core.excludesfile ~/.gitignore_global
    echo -e "${GREEN}Created global .gitignore file${NC}"
fi

# Install package managers based on OS
echo -e "\n${GREEN}Installing package managers...${NC}"
if command_exists apt-get; then
    sudo apt-get update
    sudo apt-get install -y curl wget gnupg apt-transport-https ca-certificates software-properties-common
elif command_exists yum; then
    sudo yum update -y
    sudo yum install -y curl wget gnupg2 ca-certificates
elif command_exists brew; then
    brew update
else
    echo -e "${RED}Unsupported package manager. Please install dependencies manually.${NC}"
    exit 1
fi

# Install Python if needed
echo -e "\n${GREEN}Setting up Python environment...${NC}"
if ! command_exists python3; then
    if command_exists apt-get; then
        sudo apt-get install -y python3 python3-pip python3-venv
    elif command_exists yum; then
        sudo yum install -y python3 python3-pip
    elif command_exists brew; then
        brew install python
    fi
fi

# Install Poetry
if ! command_exists poetry; then
    echo -e "${YELLOW}Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    poetry config virtualenvs.in-project true
fi

# Install pre-commit
if ! command_exists pre-commit; then
    echo -e "${YELLOW}Installing pre-commit...${NC}"
    pip3 install pre-commit
fi

# AWS CLI installation
echo -e "\n${GREEN}Setting up AWS CLI...${NC}"
if ! command_exists aws || [[ $(aws --version | grep aws-cli) != *"aws-cli/$AWS_CLI_VERSION"* ]]; then
    echo -e "${YELLOW}Installing AWS CLI v$AWS_CLI_VERSION...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip -q awscliv2.zip
        sudo ./aws/install --update
        rm -rf aws awscliv2.zip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    else
        echo -e "${RED}Unsupported OS for AWS CLI installation. Please install manually.${NC}"
    fi
fi

# Install Terraform
echo -e "\n${GREEN}Setting up Terraform...${NC}"
if ! command_exists terraform || [[ $(terraform version | head -n 1) != *"v$TERRAFORM_VERSION"* ]]; then
    echo -e "${YELLOW}Installing Terraform v$TERRAFORM_VERSION...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
        echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
        sudo apt-get update && sudo apt-get install -y terraform=$TERRAFORM_VERSION
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew tap hashicorp/tap
        brew install hashicorp/tap/terraform@$TERRAFORM_VERSION
    else
        echo -e "${RED}Unsupported OS for Terraform installation. Please install manually.${NC}"
    fi
fi

# Install TFLint
if ! command_exists tflint; then
    echo -e "${YELLOW}Installing TFLint...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install tflint
    else
        echo -e "${RED}Unsupported OS for TFLint installation. Please install manually.${NC}"
    fi
fi

# Install Docker if not present
echo -e "\n${GREEN}Setting up Docker...${NC}"
if ! command_exists docker; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    if command_exists apt-get; then
        sudo apt-get install -y docker.io
        sudo systemctl enable --now docker
        sudo usermod -aG docker $USER
        echo -e "${YELLOW}You may need to log out and back in for Docker permissions to take effect.${NC}"
    elif command_exists yum; then
        sudo yum install -y docker
        sudo systemctl enable --now docker
        sudo usermod -aG docker $USER
        echo -e "${YELLOW}You may need to log out and back in for Docker permissions to take effect.${NC}"
    elif command_exists brew; then
        brew install --cask docker
        echo -e "${YELLOW}Please start Docker Desktop from your Applications folder.${NC}"
    else
        echo -e "${RED}Unsupported OS for Docker installation. Please install manually.${NC}"
    fi
fi

# Setup AWS SSO login helper
mkdir -p ~/bin
cat > ~/bin/aws-sso-login.sh << 'EOL'
#!/bin/bash
set -e

# AWS SSO Login Helper
# Usage: aws-sso-login.sh [profile-name]

DEFAULT_PROFILE="dev"
PROFILE=${1:-$DEFAULT_PROFILE}

echo "🔐 Logging in to AWS SSO with profile: $PROFILE"
aws sso login --profile $PROFILE

# Test the credentials
echo "✅ Verifying credentials..."
aws sts get-caller-identity --profile $PROFILE

echo "✨ AWS SSO login successful!"
export AWS_PROFILE=$PROFILE
echo "🔧 Your AWS_PROFILE is now set to: $PROFILE"
EOL

chmod +x ~/bin/aws-sso-login.sh
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc

# Configure pre-commit
echo -e "\n${GREEN}Setting up pre-commit hooks...${NC}"
if [ -f .git/hooks/pre-commit ]; then
    pre-commit uninstall
fi
pre-commit install
pre-commit install --hook-type commit-msg

# Final setup
echo -e "\n${GREEN}Cloning project templates...${NC}"
mkdir -p ~/projects/templates
git clone https://github.com/example/python-api-template.git ~/projects/templates/python-api-template
git clone https://github.com/example/terraform-module-template.git ~/projects/templates/terraform-module-template

echo -e "\n${GREEN}====== Enterprise Onboarding Complete ======${NC}"
echo -e "To complete setup:"
echo -e "1. Run 'aws-sso-login.sh dev' to set up AWS access"
echo -e "2. Configure your IDE with the provided settings in .vscode/"
echo -e "3. Pull the latest Docker images with 'docker pull example/enterprise-python:latest'"
echo -e "\nFor more information, see the developer guide at: https://wiki.example.com/developer-guide"
