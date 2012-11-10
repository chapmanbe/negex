#Copyright 2010 Annie T. Chen
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
"""This middleware requires a login for every view.
"""
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login
import settings

class LoginRequiredMiddleware:
    def process_request(self, request):
        print settings.LOGIN_URL
        if request.path != settings.LOGIN_URL and request.user.is_anonymous():
            if request.POST:
                return login(request)
            else:
                return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
