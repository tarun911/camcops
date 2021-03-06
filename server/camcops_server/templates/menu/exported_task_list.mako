## exported_task_list.mako
<%inherit file="base_web.mako"/>

<%!
from markupsafe import escape
from camcops_server.cc_modules.cc_pyramid import Routes, ViewArg, ViewParam
%>

<%include file="db_user_info.mako"/>

<h1>Exported task log</h1>

%if conditions:
    <h2>Conditions</h2>
    ${conditions | h}
%endif

<h2>Results</h2>

<div>${page.pager()}</div>

<table>
    <tr>
        <th>ExportedTask</th>
        <th>Recipient</th>
        <th>Task</th>
        <th>Started at (UTC)</th>
        <th>Finished at (UTC)</th>
        <th>Success?</th>
        <th>Failure reasons</th>
        <th>Cancelled?</th>
        <th>Cancelled at (UTC)</th>
    </tr>

    %for et in page:
        <tr>
            <td><a href="${ req.route_url(Routes.VIEW_EXPORTED_TASK, _query={ViewParam.ID: et.id}) }">ExportedTask ${ et.id }</a></td>
            <td><a href="${ req.route_url(Routes.VIEW_EXPORT_RECIPIENT, _query={ViewParam.ID: et.recipient_id}) }">ExportRecipient ${ et.recipient_id }</a></td>
            <td><a href="${ req.route_url(Routes.TASK, _query={ViewParam.TABLE_NAME: et.basetable, ViewParam.SERVER_PK: et.task_server_pk, ViewParam.VIEWTYPE: ViewArg.HTML}) }">${ et.basetable } ${ et.task_server_pk }</a></td>
            <td>${ et.start_at_utc }</td>
            <td>${ et.finish_at_utc }</td>
            <td>${ et.success }</td>
            <td>${ "<br>".join(escape(reason) for reason in et.failure_reasons) | n }</td>
            <td>${ et.cancelled }</td>
            <td>${ et.cancelled_at_utc }</td>
        </tr>
    %endfor
</table>

<div>${page.pager()}</div>

<div>
    <a href="${ req.route_url(Routes.OFFER_EXPORTED_TASK_LIST)}">Choose different options</a>
</div>

<%include file="to_main_menu.mako"/>
