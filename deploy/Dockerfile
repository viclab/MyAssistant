FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY src/ .

EXPOSE 9000

CMD ["python", "app.py"]
