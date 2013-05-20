import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^pyConTextKit/index/$', 'pyConTextKit.views.index'),
    (r'^pyConTextKit/result/(?P<result_id>\d+)/$', 'pyConTextKit.views.result_detail'),
    (r'^pyConTextKit/report/(?P<reportid>\d+)/$', 'pyConTextKit.views.report_detail'),
    (r'^pyConTextKit/run/$', 'pyConTextKit.views.run'),
    (r'^pyConTextKit/complete/$', 'pyConTextKit.views.complete'),
    (r'^pyConTextKit/itemData_complete/$', 'pyConTextKit.views.itemData_complete'),
    (r'^pyConTextKit/itemData/$', 'pyConTextKit.views.itemData_view'),
    (r'^pyConTextKit/itemData_filter/(?P<cat>\w+)$', 'pyConTextKit.views.itemData_filter'),
    (r'^pyConTextKit/itemData_edit/(?P<itemData_id>\w+)$', 'pyConTextKit.views.itemData_edit'),
    (r'^pyConTextKit/itemData_edit/$', 'pyConTextKit.views.itemData_edit'),
    (r'^pyConTextKit/output_results/$', 'pyConTextKit.views.output_results'),
    (r'^pyConTextKit/reports/$', 'pyConTextKit.views.reports'),
    (r'^pyConTextKit/results/$', 'pyConTextKit.views.results'),
    (r'^pyConTextKit/stats/$', 'pyConTextKit.views.stats'),
    (r'^pyConTextKit/logout/$', 'pyConTextKit.views.logout_view'),
    url(r'^pyConTextKit/ajax_user_search/$', 'pyConTextKit.views.ajax_user_search', name = 'demo_user_search' ),
    (r'^pyConTextKit/report_text/(?P<reportid>\d+)/$', 'pyConTextKit.views.report_text'),
    (r'^pyConTextKit/$', 'pyConTextKit.views.index'),
    (r'^pyConTextKit/admin/', include(admin.site.urls)),
    (r'^pyConTextKit/accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^pyConTextKit/upload_db/(?P<formType>\w+)$', 'pyConTextKit.views.upload_csv'),
    (r'^pyConTextKit/upload_db/$', 'pyConTextKit.views.upload_csv'),
    (r'^pyConTextKit/hide/(?P<idp>\w+)/(?P<idp2>\w+)$', 'pyConTextKit.views.hide'),
    (r'^pyConTextKit/show/(?P<idp>\w+)/(?P<idp2>\w+)$', 'pyConTextKit.views.show'),
    (r'^pyConTextKit/visualize/(?P<idp>\w+)$', 'pyConTextKit.views.resultVisualize'),
    (r'^pyConTextKit/reports_index/', 'pyConTextKit.views.reports_index'),
    (r'^pyConTextKit/annotation_index/', 'pyConTextKit.views.annotation_index')
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^pyConTextKit/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

