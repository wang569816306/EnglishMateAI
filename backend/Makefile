.PHONY: help clean

# 变量定义
PORT := 8000

help: ## 显示帮助信息
	@echo "========================================="
	@echo "  FastAPI AI 服务 - Make 命令"
	@echo "========================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""


clean: ## 清理缓存文件
	@echo "🧹 清理 Python 缓存..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ 清理完成"


.DEFAULT_GOAL := help
