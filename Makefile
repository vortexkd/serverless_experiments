# Makefile
STACKNAME_BASE="hobby-scraper-dev"
# This is a region that supports AWS Fargate
REGION="us-east-1"
IMAGE_NAME="hobby-scraper"
REPOSITORY="691480986775.dkr.ecr.$(REGION).amazonaws.com"

build:
	docker build -t $(IMAGE_NAME):latest .

retag:
	docker tag $(IMAGE_NAME):latest \
		$(shell aws cloudformation --region $(REGION) describe-stacks --stack-name $(STACKNAME_BASE) --query "Stacks[0].Outputs[?OutputKey=='ECRRepo'].OutputValue" --output text):latest
	aws ecr --region $(REGION) get-login-password | docker login --username AWS --password-stdin $(REPOSITORY)
# 	@exec $(shell aws ecr --region $(REGION) get-login --no-include-email)
	docker push $(shell aws cloudformation --region $(REGION) describe-stacks --stack-name $(STACKNAME_BASE) --query "Stacks[0].Outputs[?OutputKey=='ECRRepo'].OutputValue" --output text):latest