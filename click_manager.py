
from concurrent.futures import ThreadPoolExecutor
import time
from selenium.webdriver.common.by import By
import logging

class LinuxPrecisionClickManager:
    def __init__(self, max_workers=None, logger=None):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logger or logging.getLogger(__name__)

    def _precise_sleep(self, target_time_ns):
        now = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        while now < target_time_ns:
            if target_time_ns - now > 1e-6:  # Apenas pequenos ajustes finais
                time.sleep((target_time_ns - now) / 2)
            now = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)

    def _execute_synchronized_click(self, driver, xpath, target_time_ns):
        try:
            element = driver.find_element(By.XPATH, xpath)
            if element is None:
                self.logger.warning("[Clique] Elemento não encontrado. Ignorando clique.")
                return (False, None)

            self._precise_sleep(target_time_ns)
            driver.execute_script(
                "arguments[0].dispatchEvent(new MouseEvent('click', "
                "{bubbles: true, cancelable: true, view: window}));",
                element
            )

            actual_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            deviation_ms = (actual_time - target_time_ns) * 1000
            return (True, deviation_ms)
        except Exception as e:
            self.logger.error(f"[Clique] Erro ao executar clique sincronizado: {e}")
            return (False, None)

    def execute_synchronized_clicks(self, drivers, xpaths):
        if not drivers or not xpaths:
            self.logger.error("[Clique] Drivers ou XPaths inválidos.")
            return False

        target_time_ns = time.clock_gettime(time.CLOCK_MONOTONIC_RAW) + 0.01
        results = []
        
        try:
            for driver, xpath in zip(drivers, xpaths):
                status, deviation = self._execute_synchronized_click(driver, xpath, target_time_ns)
                results.append((status, deviation))
                if deviation is not None:
                    self.logger.info(f"[Clique] Desvio no clique: {deviation:.3f}ms")
                else:
                    self.logger.info("[Clique] Clique falhou.")
            
            return all(status for status, _ in results)
        except Exception as e:
            self.logger.error(f"[Clique] Erro na execução dos cliques: {e}")
            return False

    def cleanup(self):
        if self.executor:
            self.executor.shutdown(wait=True)