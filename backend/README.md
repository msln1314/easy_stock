# 策略中心系统 - 后端

## 技术栈
- Python 3.11+
- FastAPI
- Tortoise-ORM + SQLite
- Pydantic

## 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

## 启动服务
```bash
python main.py
# 或
uvicorn main:app --reload --port 5000
```

## API文档
启动后访问: http://localhost:5000/docs