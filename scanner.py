import time
from typing import Any

from selenium.webdriver.firefox import webdriver as Firefox
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver import ActionChains


class Scanner:
    def __init__(self, origem, destino, passageiros_adulto, passageiros_crianca, data_partida, data_retorno) -> None:
        self.origem = origem
        self.destino = destino
        self.passageiros_adulto = passageiros_adulto
        self.passageiros_crianca = passageiros_crianca
        self.data_partida = data_partida
        self.data_retorno = data_retorno
        self.__configure()

    def scan(self) -> None:
        try:
            self.webdriver.get("https://b2c.voegol.com.br/compra")

            self.__fechar_politica()
            self.__definir_origem()
            self.__definir_destino()
            self.__definir_passageiros()
            self.__definir_datas()
            self.__submit()

            self.__save()
        finally:
            self.webdriver.quit()

    def __save(self) -> None:
        self.webdriver.save_full_page_screenshot("screenshot.png")

    ###############################################

    def __configure(self):
        try:
            options = Options()
            options.add_argument("--lang=pt-BR")
            options.add_argument("--disable-notifications")
            options.add_argument("ignore-error-ssl")
            options.add_argument('--headless')  # rodar em Segundo Plano
            options.headless = True
            # rodar com pouca Memoria Ram, evitando erro de performance
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')

            WINDOW_SIZE = "1920,1080"
            options.add_argument("--window-size=%s" % WINDOW_SIZE)

            firefox_profile = FirefoxProfile()
            firefox_profile.set_preference(
                "browser.privatebrowsing.autostart", True)

            binary = FirefoxBinary(
                "/Applications/Firefox.app/Contents/MacOS/firefox-bin")

            self.webdriver = Firefox.WebDriver(
                firefox_binary=binary, options=options, firefox_profile=firefox_profile)

            self.wait = WebDriverWait(
                driver=self.webdriver,
                timeout=15,
                poll_frequency=5,
                ignored_exceptions=[NoSuchElementException,
                                    ElementNotVisibleException,
                                    ElementNotSelectableException,
                                    ]
            )
        except:
            print("Erro ao configurar")
            pass

    def __get_control_by_visibility(self, query) -> Any:
        return self.wait.until(expected_conditions.visibility_of_element_located(
            (By.XPATH, query))
        )

    def __get_control_by_element(self, query) -> Any:
        return self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, query))
        )

    def __get_control_by_all_element(self, query) -> Any:
        return self.wait.until(expected_conditions.presence_of_all_elements_located(
            (By.XPATH, query))
        )

    def __fecha_dropdown(self, query) -> None:
        campo_dropdown = self.__get_control_by_all_element(query)
        time.sleep(1)
        campo_dropdown[0].click()

    def __fechar_politica(self) -> None:
        fechar_politica = self.__get_control_by_visibility(
            '//button[@id="onetrust-accept-btn-handler"]')

        if fechar_politica is not None:
            self.webdriver.execute_script(
                'arguments[0].click()', fechar_politica)
            time.sleep(2)

    def __definir_origem(self) -> None:
        saindo_de = self.__get_control_by_element(
            '//input[@id="input-saindo-de"]')

        if saindo_de is not None:
            self.webdriver.execute_script('arguments[0].click()', saindo_de)
            time.sleep(1)
            saindo_de.send_keys(self.origem)
            self.__fecha_dropdown(
                '//ul[@class="m-list-cta__list"] //li[@class="m-list-cta__item"] //button[@type="button"]')

    def __definir_destino(self) -> None:
        chegando_a = self.__get_control_by_element(
            '//input[@id="input-indo-para"]')

        if chegando_a is not None:
            self.webdriver.execute_script('arguments[0].click()', chegando_a)
            time.sleep(1)
            chegando_a.send_keys(self.destino)
            self.__fecha_dropdown(
                '//div[@class="m-dropdown__content m-dropdown--active"]  //li[@class="m-list-cta__item"]')

    def __definir_passageiros(self) -> None:
        passageiros = self.__get_control_by_visibility(
            '//fieldset[@class="a-icon a-input m-select__fieldset" and @aria-controls="counter"]')

        passageiros.click()

        if self.passageiros_adulto > 1:
            botao_adultos = self.__get_control_by_element(
                '//*[@id="counter"]/div/b2c-counter/div/div/div[1]/button[2]')

            for i in range(1, self.passageiros_adulto):
                botao_adultos.click()

        if self.passageiros_crianca > 0:
            botao_criancas = self.__get_control_by_element(
                '//*[@id="counter"]/div/b2c-counter/div/div/div[2]/button[2]')

            for i in range(0, self.passageiros_crianca):
                botao_criancas.click()

        fechar_passageiros = self.__get_control_by_element(
            '//div[@class="m-dropdown m-select__accordion--active"]'
        )

        self.webdriver.execute_script(
            'arguments[0].click()', fechar_passageiros)
        time.sleep(1)

    def __definir_datas(self) -> None:
        self.webdriver.execute_script(
            'document.getElementById("departureDate").value = "%s"' % self.data_partida)

        self.webdriver.execute_script(
            'document.getElementById("returnDate").value = "%s"' % self.data_retorno)

    def __submit(self) -> None:
        campo_enviar_informacoes = self.__get_control_by_element(
            '//button[@type="submit"]')

        # time.sleep(1)
        # self.webdriver.execute_script("arguments[0].removeAttribute('disabled')",
        #                               campo_enviar_informacoes)
        # time.sleep(1)

        # self.webdriver.execute_script(
        #     'arguments[0].click()', campo_enviar_informacoes)
        # # campo_enviar_informacoes.click()
        campo_enviar_informacoes.send_keys(Keys.RETURN)
        # campo_enviar_informacoes.send_keys(Keys.ENTER)
        # time.sleep(8)

        time.sleep(3)

        # self.wait.until(
        #     expected_conditions.visibility_of_element_located(
        #         (By.XPATH,
        #          '//span[@class="a-desc__value a-desc__value--price"]')
        #     )
        # )
