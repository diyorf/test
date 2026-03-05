from rest_framework import serializers


class RunCodeSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(required=False)
    source_code = serializers.CharField()
    stdin = serializers.CharField(required=False, allow_blank=True, default="")
