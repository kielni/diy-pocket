FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY *.py ${LAMBDA_TASK_ROOT}
RUN chmod 644 ${LAMBDA_TASK_ROOT}/*.py

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ] 