#!/bin/python3
import time
from random import randrange
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 3)
    global proxies
    proxies = {
        'http': 'http://squid-proxy-nlb-ebd8e71852a19d45.elb.us-gov-west-1.amazonaws.com:3128',
        'https': 'http://squid-proxy-nlb-ebd8e71852a19d45.elb.us-gov-west-1.amazonaws.com:3128',
    }
    # mock app index
    @task(10)
    def getSSM(self):
        self.client.get("https://s3.us-gov-west-1.amazonaws.com/amazon-ssm-us-gov-west-1/latest/linux_amd64/amazon-ssm-agent.rpm", name="ssmAgentDownload", proxies=proxies)
        time.sleep(randrange(1,10))

    # # mock app get pets
    # @task(2)
    # def getPets(self):
    #     for petId in range(1,100):
    #         self.client.get(f"https://rndrj09dmf.execute-api.us-gov-east-1.amazonaws.com/calamari/pets/{petId}", name="pets", proxies=proxies)
    #         time.sleep(randrange(1,5))

    # # mock app post pets
    # @task(3)
    # def postPets(self):
    #     petTypes = [ "dog", "cat", "fish", "bird", "gecko" ]
    #     for pType in petTypes:
    #         self.client.post("https://rndrj09dmf.execute-api.us-gov-east-1.amazonaws.com/calamari/pets", json={"type":f"{pType}", "price":139.99}, name="petsPost", proxies=proxies)
    #         time.sleep(randrange(1,5))
    # # amazon aws check ip
    @task()
    def getAmazon(self):
        self.client.get("https://checkip.amazonaws.com", name="checkip", proxies=proxies)
        time.sleep(randrange(1,5))
    # google news
    @task()
    def getGoogle(self):
        self.client.get("https://news.google.com/topstories?tab=rn&hl=en-US&gl=US&ceid=US:en", name="google", proxies=proxies)
        time.sleep(randrange(1,5))
    # yahoo finance
    @task()
    def getYahoo(self):
        self.client.get("https://finance.yahoo.com", name="yahoo", proxies=proxies)
        time.sleep(randrange(1,5))
    # get facebook.com, expected block
    @task()
    def getFacebook(self):
        self.client.get("https://facebook.com", name="facebook", proxies=proxies)
        time.sleep(randrange(1,5))