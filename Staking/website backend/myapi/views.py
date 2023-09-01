from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from .scripts import tongochi_db
from .serializers import PoolSerializer, StakerSerializer
from .models import Pool, Staker


class MethodsView(APIView):
    def get(self, request: Request):
        possible_urls = list(map(lambda x: "https://api.tongochi.org/stakingapi/" + x,
                                 ["pools/", "stakers/", "dev-points/", "nft/content/"]))
        return Response(status=200, data={"Possible urls:": possible_urls})


class PoolView(APIView):

    def get(self, request: Request):
        name = request.GET.get("name")
        if name:
            res = Pool.objects.get(name=name)
            if res:
                serializer = PoolSerializer(res)
                return Response(status=200, data=serializer.data)  # {"status": "OK", "data": serializer.data})
            return Response(status=404, data={"Error": "Pool not found"})
        else:
            res = Pool.objects.all()
            serializer = PoolSerializer(res, many=True)
            return Response(status=200, data=serializer.data)


class StakerView(APIView):

    def get(self, request: Request):
        stakerAddress = request.GET.get("stakerAddress")
        poolName = request.GET.get("poolName")
        res = Staker.objects.all()
        if stakerAddress:
            res = res.filter(stakerAddress=stakerAddress)
        if poolName:
            res = res.filter(poolName=poolName)
        if res:
            serializer = StakerSerializer(res, many=True)
            return Response(status=200, data=serializer.data)
        else:
            return Response(status=404, data={"Error": "Staker not found"})


class DeveloperPointsView(APIView):

    def get(self, request: Request):
        wallet = request.GET.get("wallet")

        if wallet is None:
            response_data = {"Error": "Missing required argument 'wallet'"}
            return Response(status=404, data=response_data)

        points = tongochi_db.get_developer_points(wallet_address=wallet)
        amount_of_points, devider, last_update_amount = points

        response_data = {
            'amount_of_points': amount_of_points,
            'devider': devider,
            'last_update_amount': last_update_amount,
            'price_per_one_coupon': 1000,
        }
        return Response(status=200, data=response_data)


class NftView(APIView):
    def get(self, request: Request):
        collection = request.GET.get("collection")
        filename = request.GET.get("filename")

        if collection is None:
            response_data = {"Error": "Missing required argument 'collection'"}
            return Response(status=404, data=response_data)
        if filename is None:
            response_data = {"Error": "Missing required argument 'filename'"}
            return Response(status=404, data=response_data)

        item_index = int(filename.split('.')[0])
        response_data = tongochi_db.get_nft_item(collection, item_index)

        return Response(status=200, data=response_data)
