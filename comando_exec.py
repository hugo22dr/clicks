from log_config import get_logger  # Centraliza logs
from navegador_op import (
    verificar_e_restaurar_sessao, 
    localizar_elementos_em_abas,
    clicar_elementos_em_navegador,
)
from click_manager import LinuxPrecisionClickManager
  # Importa o gerenciador de cliques
from config import drivers, navegadores_config, validar_configuracao

# Logger para este módulo
logger = get_logger(__name__)

def executar_comando_new_link(drivers, navegadores_config):
    for index, driver in enumerate(drivers):
        if driver is None or not driver.session_id:
            logger.warning(f"[Navegador {index + 1}] Sessão inválida. Pule este navegador.")
            continue
        novo_link = input(f"Digite o novo link para o navegador {index + 1}: ").strip()
        if novo_link:
            try:
                logger.info(f"[Navegador {index + 1}] Carregando link: {novo_link}")
                driver.get(novo_link)
                navegadores_config[index]["link"] = novo_link
                navegadores_config[index]["xpaths"] = []
                logger.info(f"[Navegador {index + 1}] Link configurado com sucesso.")
            except Exception as e:
                logger.error(f"[Navegador {index + 1}] Erro ao carregar o link: {e}")
        else:
            logger.warning(f"[Navegador {index + 1}] Nenhum link fornecido. Pulando.")

def executar_comando_add(drivers, navegadores_config):
    for index, driver in enumerate(drivers):
        config = navegadores_config[index]
        if not config["link"]:
            logger.warning(f"[Navegador {index + 1}] Nenhum link configurado. Pule este navegador.")
            continue
        novo_xpath = input(f"Digite um novo XPath para o navegador {index + 1}: ").strip()
        if novo_xpath:
            if novo_xpath.startswith("//") or novo_xpath.startswith(".//"):
                config["xpaths"].append(novo_xpath)
                logger.info(f"[Navegador {index + 1}] Novo XPath adicionado: {novo_xpath}")
            else:
                logger.warning(f"[Navegador {index + 1}] XPath inválido: {novo_xpath}")
        else:
            logger.info(f"[Navegador {index + 1}] Nenhum XPath foi adicionado.")

def executar_cliques_simultaneos(drivers, navegadores_config):
    logger.info("[Clique] Iniciando execução de cliques sincronizados...")
    navegadores_validos = validar_configuracao()
    if not navegadores_validos:
        logger.warning("[Clique] Nenhum navegador configurado corretamente para executar cliques.")
        return

    # Coletar apenas os XPaths configurados
    xpaths_por_driver = [
        navegadores_config[index]["xpaths"][0]  # Apenas o primeiro XPath de cada navegador
        for index in navegadores_validos
    ]

    if xpaths_por_driver:
        logger.info("[Clique] Executando cliques sincronizados...")
        click_manager = LinuxPrecisionClickManager(max_workers=len(navegadores_validos))
        resultados = click_manager.execute_synchronized_clicks(
            [drivers[i] for i in navegadores_validos], xpaths_por_driver
        )
        if all(resultados):
            logger.info("[Clique] Todos os cliques foram bem-sucedidos.")
        else:
            logger.warning("[Clique] Alguns cliques falharam.")
    else:
        logger.warning("[Clique] Nenhum elemento válido para clique.")
def executar_comando_localize(drivers, navegadores_config):
    for index, driver in enumerate(drivers):
        config = navegadores_config[index]
        if not config["link"] or not config["xpaths"]:
            logger.warning(f"[Navegador {index + 1}] Não configurado corretamente. Pulando.")
            continue
        try:
            encontrados = localizar_elementos_em_abas(driver, index, config["xpaths"])
            if encontrados:
                logger.info(f"[Navegador {index + 1}] Elementos encontrados: {len(encontrados)}")
            else:
                logger.warning(f"[Navegador {index + 1}] Nenhum elemento localizado.")
        except Exception as e:
            logger.error(f"[Navegador {index + 1}] Erro ao localizar elementos: {e}")

def executar_comando(comando, drivers, navegadores_config):
    if comando == "new link":
        executar_comando_new_link(drivers, navegadores_config)
    elif comando == "add":
        executar_comando_add(drivers, navegadores_config)
    elif comando == "click":
        executar_cliques_simultaneos(drivers, navegadores_config)
    elif comando == "localize":
        executar_comando_localize(drivers, navegadores_config)
    else:
        logger.warning("[Sistema] Comando inválido.")
