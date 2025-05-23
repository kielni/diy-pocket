.PHONY: clean build deploy update-lambda

# Load environment variables if .env file exists
-include local.env

# Configuration with defaults
FUNCTION_NAME ?= diy-pocket-save
RUNTIME = python3.9
HANDLER = lambda_function.lambda_handler
MEMORY = 128
TIMEOUT = 30


# on update
build: clean 
	mkdir -p package
	pip install --target ./package -r requirements.txt
	cp lambda_function.py package/
	cd package && zip -r ../deployment-package.zip .
	@echo "Created deployment package: deployment-package.zip"

build-py: 
	cp lambda_function.py package/
	cd package && zip -r ../deployment-package.zip .
	@echo "Created deployment package: deployment-package.zip"


update:
	aws lambda update-function-code \
		--function-name $(FUNCTION_NAME) \
		--zip-file fileb://deployment-package.zip


clean:
	rm -rf package deployment-package.zip
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# one time setup
setup-lambda: build
	aws lambda create-function \
		--function-name $(FUNCTION_NAME) \
		--runtime $(RUNTIME) \
		--handler $(HANDLER) \
		--memory-size $(MEMORY) \
		--timeout $(TIMEOUT) \
		--role $(ROLE_ARN) \
		--zip-file fileb://deployment-package.zip

setup-api:
	@echo "Creating API Gateway REST API..."
	aws apigateway create-rest-api \
		--name "DIY Pocket API" \
		--description "API for DIY Pocket Lambda"

lint:
	black *.py
	flake8 *.py