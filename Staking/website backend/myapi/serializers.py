from rest_framework import serializers

from .models import Pool, Staker


class PoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pool
        fields = ('name', 'contractAddress', 'jettonWalletAddress', 'stonfiPoolAddress',
                  'jettonType', 'jettonTvl', 'tonTvl', 'usdTvl', 'testnet', 'category')

    def update(self, instance, validated_data):
        instance.contractAddress = validated_data.get("contractAddress", instance.contractAddress)
        instance.jettonWalletAddress = validated_data.get("jettonWalletAddress", instance.jettonWalletAddress)
        instance.stonfiPoolAddress = validated_data.get("stonfiPoolAddress", instance.stonfiPoolAddress)
        instance.jettonType = validated_data.get("jettonType", instance.jettonType)
        instance.jettonTvl = validated_data.get("jettonTvl", instance.jettonTvl)
        instance.tonTvl = validated_data.get("tonTvl", instance.tonTvl)
        instance.usdTvl = validated_data.get("usdTvl", instance.usdTvl)
        instance.testnet = validated_data.get("testnet", instance.testnet)
        instance.category = validated_data.get("category", instance.category)
        instance.save()
        return instance


class StakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staker
        fields = ("id", "stakerAddress", "poolName", "stakedJettons",
                  "tonEquivalent", "stakerNftItems", "testnet")
