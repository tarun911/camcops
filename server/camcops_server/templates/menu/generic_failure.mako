## general_failure.mako
<%inherit file="base_web.mako"/>

<%include file="db_user_info.mako"/>

%if msg:
    <h2 class="error">${msg | h}</h2>
%endif

%if extra_html:
    ${extra_html}
%endif

${parent.body()}

<div class="error">
    %if request.user_id is None:
        <%block go_to_login>
            <div>
                Click <a href="${request.route_url(Routes.LOGIN)}">here</a> to log in.
            </div>
        </%block>
    %else:
        <%include file="to_main_menu.mako"/>
    %endif
</div>
