from django.shortcuts import render, redirect
from flutterwave import Flutterwave
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages


def initialize_flw(api_key, merchant_key):    
    flw = Flutterwave(api_key, merchant_key, {"debug": False})
    return flw

def retrieve_values(request):
    '''Retrieve saved values from session'''
    api_key                                 = request.session['api_key']              
    merchant_key                            = request.session['merchant_key']
    verifyUsing                             = request.session['verifyUsing']
    country                                 = request.session['country']
    transactionReference                    = request.session['transactionReference'] 
    bvn                                     = request.session['bvn']    
    
    return api_key, merchant_key, verifyUsing, country, transactionReference, bvn

def clear_values_from_session(request, keys_list):
    for key in keys_list:
        if request.session.has_key(key):
            del request.session['key']
            
            
def verify(request):
    '''Verify'''
    
    if request.method == "POST":
        print request.POST
        print 'posting to verify_bvn'
        
        bvn                     = request.POST.get('bvn_no')
        verifyUsing             = request.POST.get('verifyUsing')
        country                 = request.POST.get('country')
        
        api_key                 = request.POST.get('api_key')
        merchant_key            = request.POST.get('merchant_key')
        
        flw                     = initialize_flw(api_key, merchant_key)
        
        verify                  = flw.bvn.verify(bvn, verifyUsing, country)
        verify_json             = verify.json()
        
        responseMessage         = verify_json['data']['responseMessage']
        
        print 'verify_json: ',verify_json
        
        if responseMessage == 'Successful, pending OTP validation':
            
            transactionReference    = verify_json['data']['transactionReference']
            
            '''Keep important variables in session, for later use'''
            request.session['api_key']              = api_key
            request.session['merchant_key']         = merchant_key
            request.session['verifyUsing']          = verifyUsing
            request.session['country']              = country
            request.session['transactionReference'] = transactionReference
            request.session['bvn']                  = bvn
            
            return redirect(reverse('enter_otp'))
    
        messages.error(request, 'Ooops! %s' %responseMessage) 
    return render(request, 'bvn/verify_bvn.html')
    
    
    
def resend_opt(request):
    '''Resend OTP'''
    
    '''Retrieve saved values from session'''
    api_key, merchant_key, verifyUsing, country, transactionReference, bvn  = retrieve_values(request)
        
    flw                                     = initialize_flw(api_key, merchant_key)
    resend_opt                              = flw.bvn.resendOtp(verifyUsing, transactionReference, country)
    resend_opt_json                         = resend_opt.json()
    print 'resend_opt_json: ',resend_opt_json
    
    return JsonResponse({'status': resend_opt_json['status']})


def enter_otp(request):
    
    if request.session.has_key('bvn') and request.session.has_key('verifyUsing'):
        context = {'bvn': request.session['bvn'], 'verifyUsing': request.session['verifyUsing']}
        return render(request, 'bvn/enter_otp_for_bvn.html', context)
    
    return redirect(reverse('verify_bvn'))

def validation_result(request):
    context = {}
    '''Validate BVN'''
    if request.method == "POST":
        otp = request.POST.get('otp')
        
        '''Retrieve saved values from session'''
        api_key, merchant_key, verifyUsing, country, transactionReference, bvn  = retrieve_values(request)           
        
        flw                                     = initialize_flw(api_key, merchant_key)
        validate                                = flw.bvn.validate(bvn, otp, transactionReference, country)
        validate_json                           = validate.json()
        
        print 'validate_json: ',validate_json
        
        context.update({'data': validate_json['data']})
        
        '''Clear saved values from session'''
        keys_list = ['api_key', 'merchant_key', 'verifyUsing', 'country', 'transactionReference', 'bvn']
        clear_values_from_session(request, keys_list)
        
    return render(request, 'bvn/bvn_verification_result.html', context)
    
    return redirect(reverse('bvn/enter_otp_for_bvn'))
    #return HttpResponse("{}".format(validate.text))
    
    