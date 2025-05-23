.PHONY: clean build deploy update-lambda

# Load environment variables if .env file exists
-include local.env

# Configuration with defaults
FUNCTION_NAME ?= diy-pocket-save
RUNTIME = python3.9
HANDLER = main.lambda_handler
MEMORY = 128
TIMEOUT = 30

# Validate required environment variables
check-env:
ifndef ROLE_ARN
	$(error ROLE_ARN is not set. Please set it in .env file or environment)
endif

# on update
build: clean
	mkdir -p package
	pip install --target ./package -r requirements.txt
	cp main.py package/
	cd package && zip -r ../deployment-package.zip .
	@echo "Created deployment package: deployment-package.zip"

update-lambda: check-env build
	aws lambda update-function-code \
		--function-name $(FUNCTION_NAME) \
		--zip-file fileb://deployment-package.zip


clean:
	rm -rf package deployment-package.zip
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete


setup-api:
	@echo "Creating API Gateway REST API..."
	aws apigateway create-rest-api \
		--name "DIY Pocket API" \
		--description "API for DIY Pocket Lambda"

