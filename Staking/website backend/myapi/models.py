from django.db import models


class Pool(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    contractAddress = models.CharField(max_length=60)
    jettonWalletAddress = models.CharField(max_length=60)
    stonfiPoolAddress = models.CharField(max_length=60)
    jettonType = models.CharField(max_length=6, choices=(("LP", "LP"), ("Jetton", "Jetton")))
    jettonTvl = models.BigIntegerField(default=0, null=True)
    tonTvl = models.FloatField(default=0)
    usdTvl = models.FloatField(default=0)
    testnet = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Staker(models.Model):
    id = models.IntegerField(primary_key=True)
    stakerAddress = models.CharField(max_length=60)
    poolName = models.CharField(max_length=20)
    stakedJettons = models.BigIntegerField(default=0)
    tonEquivalent = models.FloatField(default=0)
    stakerNftItems = models.JSONField(default=dict)
    testnet = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
