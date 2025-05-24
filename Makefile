.PHONY: clean build update lint

# Load environment variables if .env file exists
-include local.env

# Configuration with defaults
FUNCTION_NAME ?= diy-pocket-save
AWS_REGION ?= us-east-1
ECR_REPO ?= $(FUNCTION_NAME)
IMAGE_TAG ?= "$(FUNCTION_NAME)-latest"


build:
	@echo "Building Docker image $(FUNCTION_NAME):$(IMAGE_TAG)..."
	docker build -t $(FUNCTION_NAME):$(IMAGE_TAG) .

login:
	aws ecr get-login-password --region $(AWS_REGION) | \
	docker login --username AWS --password-stdin $(ECR_REPO)

update:
	@repo=$$(echo $(ECR_REPO) | cut -d '/' -f 2); \
	digest=$$(aws ecr describe-images \
		--repository-name $$repo \
		--image-ids imageTag=$(IMAGE_TAG) \
		--query 'imageDetails[0].imageDigest' \
		--output text); \
	aws ecr batch-delete-image \
		--repository-name $$repo \
		--image-ids imageDigest=$$digest
	docker tag $(FUNCTION_NAME):$(IMAGE_TAG) $(ECR_REPO):$(IMAGE_TAG)
	docker push $(ECR_REPO):$(IMAGE_TAG)
	aws lambda update-function-code \
		--function-name $(FUNCTION_NAME) \
		--image-uri $(ECR_REPO):$(IMAGE_TAG)

lint:
	black *.py
	flake8 *.py