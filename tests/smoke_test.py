# a quick smoke to see if URLs throw exceptions or not

def run():
    ''' run with ./manage.py runscript tests.smoke_test '''
    
    from django.test.client import Client
    c = Client()
    
    pages = [
        '/',
    ]
    
    for page in pages:
        print page,
        try:
            x = c.get(page)
            if x.status_code in [301, 302]:
                print x.status_code, "=>", x["Location"]
            else:
                print x.status_code
                
        except Exception, e:
            print e
