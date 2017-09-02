## introspection_file_list.mako
<%inherit file="base_web.mako"/>

<%include file="db_user_info.mako"/>

<h1>Introspection into CamCOPS source code</h1>

%for ifd in ifd_list:
    <div>
        <a href="${request.route_url(Routes.INTROSPECT, _query=dict(filename=ifd.prettypath))}">${ifd.prettypath}</a>
    </div>
%endfor
