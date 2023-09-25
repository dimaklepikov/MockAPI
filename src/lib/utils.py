from typing import List
from app import cfg
import os
import pdb

from src.lib.i18n import Message as m

class Utils:
    def __init__(self) -> None:
        self.msg = m()
        

    def check(self):
        hostname = cfg['bind']['host']
        response = os.system("ping -c 1 " + hostname)
        if response == 0:
            pingstatus = "Network Active"
        else:
            pingstatus = "Network Error"
        return pingstatus

    def get_paginated_response(self, obj: List, per_page=10, page=1):
        # result = None
        if per_page > len(obj):
            if len(obj) == 0:
                return {
                    "message": self.msg.get('user.missing')
                }, 400
            result = [obj[i:i+len(obj)] for i in range(0, len(obj), len(obj))]
        else:
            result = [obj[i:i+per_page] for i in range(0, len(obj), per_page)]
        if page > len(result):
            return {
                "message": self.msg.get('page.invalid'),
                "total_pages": len(result),
            }, 400
        return {
            "page": page,
            "per_page": per_page,
            "total_pages": len(result),
            "data": result[page-1]
        }, 200
