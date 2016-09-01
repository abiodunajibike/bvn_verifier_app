
from django.conf.urls import include, url

import views

urlpatterns = [
    
    url(r'^verify', views.verify, name="verify"),
    url(r'^enter-otp', views.enter_otp, name="enter_otp"),
    url(r'^resend-opt', views.resend_opt, name="resend_opt"),
    url(r'^validation-result', views.validation_result, name="validation_result"),

]
