## developer.mako
<%inherit file="base_web.mako"/>

<%!
from camcops_server.cc_modules.cc_pyramid import Routes, ViewArg, ViewParam
%>

<h2>Developer test pages</h2>

<h3>Basic HTTP</h3>
<ul>
    <li><a href="${request.route_url(Routes.TESTPAGE_PUBLIC_1)}">Public test page 1</a> (plain)</li>
    <li><a href="${request.route_url(Routes.TESTPAGE_PRIVATE_1)}">Private test page 1</a> (plain)</li>
    <li><a href="${request.route_url(Routes.TESTPAGE_PRIVATE_2)}">Private test page 2</a> (<b>sensitive</b> variables)</li>
    <li><a href="${request.route_url(Routes.TESTPAGE_PRIVATE_3)}">Private test page 3</a> (template inheritance)</li>
    <li><a href="${request.route_url(Routes.CRASH)}">Deliberately crash the request</a> (shouldn’t crash the server!)</li>
</ul>

<h3>Index testing</h3>
<ul>
    <li><a href="${request.route_url(Routes.VIEW_TASKS, _query={
                ViewParam.VIA_INDEX: False
            }) }">View tasks without using index</a></li>
    <li>Trackers and CTVs have a no-index option available to users directly.</li>
</ul>
