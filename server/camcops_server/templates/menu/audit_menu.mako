## audit_menu.mako
<%inherit file="base_web.mako"/>

<%!
from camcops_server.cc_modules.cc_pyramid import Routes
%>

<h2>Audit options</h2>

<h3>Access logs</h3>
<ul>
    <li><a href="${request.route_url(Routes.OFFER_AUDIT_TRAIL)}">Audit trail</a></li>
</ul>

<h3>Export logs</h3>
<ul>
    <li><a href="${request.route_url(Routes.OFFER_EXPORTED_TASK_LIST)}">Exported task log</a></li>
</ul>
