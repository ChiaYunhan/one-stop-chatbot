#!/bin/bash

# Bash Script for Lambda Layer Creator
# Usage: ./create-layer.sh -n "layer-name" -p "boto3,requests,pandas"
# or: ./create-layer.sh --name "layer-name" --packages "boto3,requests"

set -e  # Exit on any error

# Default values
LAYER_NAME=""
PACKAGES="boto3,requests"
PYTHON_VERSIONS="python3.12"
KEEP_TEMP_DIR=true
CLEANUP_TEMP=false
PIP_ARGS=""
HELP=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show help
show_help() {
    cat << EOF
Lambda Layer Creator for AWS

USAGE:
    $0 -n LAYER_NAME [-p PACKAGES] [-v PYTHON_VERSIONS] [-a PIP_ARGS] [-c] [-h]

OPTIONS:
    -n, --name LAYER_NAME       Name of the Lambda layer (required)
    -p, --packages PACKAGES     Comma-separated list of Python packages (default: boto3,requests)
    -v, --python-versions VERSIONS  Comma-separated Python versions (default: python3.12)
    -a, --pip-args ARGS         Additional pip install arguments
    -c, --cleanup               Remove temporary directory after creating zip (default: keep directory)
    -h, --help                  Show this help message

EXAMPLES:
    $0 -n "aws-utils"
    $0 -n "data-processing" -p "pandas,numpy,openpyxl"
    $0 -n "web-scraping" -p "requests,beautifulsoup4,lxml"
    $0 -n "custom-layer" -p "requests==2.31.0,boto3" -a "--no-cache-dir"
    $0 -n "debug-layer" -p "boto3" -c

REQUIREMENTS:
    - Python 3.x with pip
    - zip command
    - AWS CLI (optional, for uploading)

NOTE:
    By default, both the directory structure and zip file are kept.
    Use -c/--cleanup to remove the directory and keep only the zip file.

EOF
}

# Function to validate layer name
validate_layer_name() {
    local name=$1
    if [[ -z "$name" ]]; then
        print_color $RED "Error: Layer name is required"
        show_help
        exit 1
    fi
    
    # Check for invalid characters using a safer approach
    if [[ "$name" =~ [[:space:]] ]] || [[ "$name" == *"<"* ]] || [[ "$name" == *">"* ]] || \
       [[ "$name" == *":"* ]] || [[ "$name" == *"\""* ]] || [[ "$name" == *"|"* ]] || \
       [[ "$name" == *"?"* ]] || [[ "$name" == *"*"* ]] || [[ "$name" == *"/"* ]] || \
       [[ "$name" == *"\\"* ]]; then
        print_color $RED "Error: Layer name contains invalid characters. Use only letters, numbers, hyphens, and underscores."
        exit 1
    fi
}

# Function to check dependencies
check_dependencies() {
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_color $RED "Error: Python is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_color $RED "Error: pip is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v zip &> /dev/null; then
        print_color $RED "Error: zip command is not installed"
        exit 1
    fi
}

# Function to get pip command (pip or pip3)
get_pip_command() {
    if command -v pip3 &> /dev/null; then
        echo "pip3"
    elif command -v pip &> /dev/null; then
        echo "pip"
    else
        print_color $RED "Error: No pip command found"
        exit 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            LAYER_NAME="$2"
            shift 2
            ;;
        -p|--packages)
            PACKAGES="$2"
            shift 2
            ;;
        -v|--python-versions)
            PYTHON_VERSIONS="$2"
            shift 2
            ;;
        -a|--pip-args)
            PIP_ARGS="$2"
            shift 2
            ;;
        -c|--cleanup)
            CLEANUP_TEMP=true
            KEEP_TEMP_DIR=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_color $RED "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate inputs
validate_layer_name "$LAYER_NAME"
check_dependencies

# Convert comma-separated packages to array
IFS=',' read -ra PACKAGE_ARRAY <<< "$PACKAGES"

# Create safe directory and file names
TEMP_DIR_NAME="$LAYER_NAME"
OUTPUT_FILE_NAME="$LAYER_NAME.zip"
PYTHON_DIR="$TEMP_DIR_NAME/python"

print_color $GREEN "Creating Lambda Layer: $LAYER_NAME"
print_color $CYAN "Packages to install: ${PACKAGE_ARRAY[*]}"

# Create directory structure
print_color $YELLOW "Creating directory structure..."
mkdir -p "$PYTHON_DIR"

# Install packages
print_color $YELLOW "Installing packages..."

PIP_CMD=$(get_pip_command)
INSTALL_CMD="$PIP_CMD install ${PACKAGE_ARRAY[*]} -t $PYTHON_DIR"

if [[ -n "$PIP_ARGS" ]]; then
    INSTALL_CMD="$INSTALL_CMD $PIP_ARGS"
fi

print_color $GRAY "Running: $INSTALL_CMD"

if ! $INSTALL_CMD; then
    print_color $RED "Error: Failed to install packages"
    [[ -d "$TEMP_DIR_NAME" ]] && rm -rf "$TEMP_DIR_NAME"
    exit 1
fi

# Create requirements.txt with exact versions
print_color $YELLOW "Generating requirements.txt for the layer..."

REQ_FILE="$TEMP_DIR_NAME/requirements.txt"

# Freeze only packages installed into python/
if $PIP_CMD freeze --path "$PYTHON_DIR" > "$REQ_FILE"; then
    print_color $GREEN "Created: $REQ_FILE"
else
    print_color $RED "Warning: Failed to generate requirements.txt"
fi

# Create zip file
print_color $YELLOW "Creating zip file..."

if ! (cd "$TEMP_DIR_NAME" && zip -r "../$OUTPUT_FILE_NAME" python/); then
    print_color $RED "Error: Failed to create zip file"
    [[ -d "$TEMP_DIR_NAME" ]] && rm -rf "$TEMP_DIR_NAME"
    exit 1
fi

# Get file size info
if [[ -f "$OUTPUT_FILE_NAME" ]]; then
    FILE_SIZE_BYTES=$(stat -c%s "$OUTPUT_FILE_NAME" 2>/dev/null || stat -f%z "$OUTPUT_FILE_NAME" 2>/dev/null || echo "0")
    FILE_SIZE_MB=$(echo "scale=2; $FILE_SIZE_BYTES / 1024 / 1024" | bc -l 2>/dev/null || echo "0")
    FILE_SIZE_KB=$(echo "scale=0; $FILE_SIZE_BYTES / 1024" | bc -l 2>/dev/null || echo "0")
else
    print_color $RED "Error: Output file was not created"
    exit 1
fi

print_color $GREEN "\nLambda layer created successfully!"
print_color $NC "File: $OUTPUT_FILE_NAME"
print_color $NC "Size: ${FILE_SIZE_MB} MB (${FILE_SIZE_KB} KB)"

# Show what was created
print_color $CYAN "\nCreated files:"
print_color $NC "  📦 $OUTPUT_FILE_NAME (zip file for AWS upload)"
if [[ "$CLEANUP_TEMP" == false ]]; then
    print_color $NC "  📁 $TEMP_DIR_NAME/ (directory structure)"
    print_color $NC "     └── python/ (packages installed here)"
fi

# Show package versions
print_color $CYAN "\nInstalled package versions:"
for package in "${PACKAGE_ARRAY[@]}"; do
    # Extract package name (remove version specifiers like ==2.31.0)
    clean_package=$(echo "$package" | sed 's/[>=<~!].*//')
    version_info=$($PIP_CMD show "$clean_package" 2>/dev/null | grep "Version:" || echo "Version: unavailable")
    print_color $NC "   $clean_package: $(echo "$version_info" | cut -d' ' -f2)"
done

# AWS CLI command suggestion
print_color $YELLOW "\nAWS CLI upload command:"
# Convert comma-separated python versions to space-separated
PYTHON_RUNTIMES=$(echo "$PYTHON_VERSIONS" | tr ',' ' ')
AWS_COMMAND="aws lambda publish-layer-version --layer-name $LAYER_NAME --description \"Lambda layer with ${PACKAGE_ARRAY[*]}\" --zip-file fileb://$OUTPUT_FILE_NAME --compatible-runtimes $PYTHON_RUNTIMES"
print_color $GRAY "$AWS_COMMAND"

# Usage example
print_color $YELLOW "\nUsage in Lambda function:"
print_color $NC "   Add the layer ARN to your Lambda function, then import normally:"
for package in "${PACKAGE_ARRAY[@]}"; do
    clean_package=$(echo "$package" | sed 's/[>=<~!].*//')
    print_color $GRAY "   import $clean_package"
done

# Directory usage info
if [[ "$CLEANUP_TEMP" == false ]]; then
    print_color $YELLOW "\nLocal development:"
    print_color $NC "   You can test packages locally using the $TEMP_DIR_NAME/ directory:"
    print_color $GRAY "   export PYTHONPATH=\"\$PWD/$TEMP_DIR_NAME/python:\$PYTHONPATH\""
    print_color $GRAY "   python3 -c \"import ${PACKAGE_ARRAY[0]}; print('${PACKAGE_ARRAY[0]} works!')\""
fi

# Handle cleanup
if [[ "$CLEANUP_TEMP" == true ]]; then
    rm -rf "$TEMP_DIR_NAME"
    print_color $GRAY "\nCleaned up temporary directory (keeping only zip file)"
else
    print_color $GRAY "\nDirectory structure preserved: $TEMP_DIR_NAME/"
    print_color $GRAY "Use -c/--cleanup flag if you only want the zip file"
fi

print_color $GREEN "\nLayer creation complete!"