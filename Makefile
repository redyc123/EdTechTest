up:
	@echo "Введи название сервиса" \ 
	@read NAME; \
		docker compose --env-file .env up $$NAME --build --detach --force-recreate