## user_info_detail.mako
<%page args="user: User"/>

<%!

from camcops_server.cc_modules.cc_html import get_yes_no
from camcops_server.cc_modules.cc_pyramid import Routes, ViewArg, ViewParam

%>

<%namespace file="displayfunc.mako" import="one_per_line"/>

<h2>Core information</h2>

<table>
    <tr>
        <th>Username</th>
        <td>${ user.username | h }</td>
    </tr>
    <tr>
        <th>User ID</th>
        <td>${ user.id }</td>
    </tr>
    <tr>
        <th>Full name</th>
        <td>${ (user.fullname or "") | h }</td>
    </tr>
    <tr>
        <th>E-mail address</th>
        <td>${ (user.email or "") | h }</td>
    </tr>
    <tr>
        <th>Last login at (UTC)</th>
        <td>${ user.last_login_at_utc }</td>
    </tr>
    <tr>
        <th>Locked out?</th>
        <td>${ get_yes_no(request, user.is_locked_out(request)) }</td>
    </tr>
    <tr>
        <th>Last password change (UTC)</th>
        <td>${ user.last_password_change_utc }</td>
    </tr>
    <tr>
        <th>Must change password at next login?</th>
        <td>${ get_yes_no(request, user.must_change_password) }</td>
    </tr>
    <tr>
        <th>Agreed to terms of use at:</th>
        <td>${ user.when_agreed_terms_of_use }</td>
    </tr>
    <tr>
        <th>Superuser?</th>
        <td ${ ('class="important"' if user.superuser else "") }>
            ${ get_yes_no(request, user.superuser) }
        </td>
    </tr>
</table>

<h2>Summary of group membership information</h2>

<table>
    <tr>
        <th>May log in to web viewer?</th>
        <td>${ get_yes_no(request, user.may_use_webviewer) }</td>
    </tr>
    <tr>
        <th>May register new tablet devices?</th>
        <td>${ get_yes_no(request, user.may_register_devices) }</td>
    </tr>
    <tr>
        <th>Groups this user is a member of:</th>
        <td>
            <%
                groups = list(user.groups)
                groups.sort(key=lambda g: g.name)
            %>
            ${ one_per_line(g.name for g in groups) }
        </td>
    </tr>
    <tr>
        <th>Groups this user is an administrator for:</th>
        <td class="important">
            ${ one_per_line(g.name for g in user.groups_user_is_admin_for) }
        </td>
    </tr>
    <tr>
        <th>Groups this user can see data from:</th>
        <td>
            ${ one_per_line(g.name for g in user.groups_user_may_see) }
        </td>
    </tr>
    <tr>
        <th>Groups this user can see all patients from, when no task filters
            are applied? (For other groups, only anonymous tasks will be shown
            if no patient filters are applied.)</th>
        <td>
            ${ one_per_line(g.name for g in user.groups_user_may_see_all_pts_when_unfiltered) }
        </td>
    </tr>
    <tr>
        <th>Groups this user can upload into:</th>
        <td>
            ${ one_per_line(g.name for g in user.groups_user_may_upload_into) }
        </td>
    </tr>
    <tr>
        <th>Groups this user may add special notes to tasks for:</th>
        <td>
            ${ one_per_line(g.name for g in user.groups_user_may_add_special_notes) }
        </td>
    </tr>
    <tr>
        <th>Groups this user can dump data from:</th>
        <td>
            ${ one_per_line(g.name for g in user.groups_user_may_dump) }
        </td>
    </tr>
    <tr>
        <th>Groups this user can run reports on:</th>
        <td>
            ${ one_per_line(g.name for g in user.groups_user_may_report_on) }
        </td>
    </tr>
    <tr>
        <th>Group this user is currently set to upload into:</th>
        <td>
            %if user.upload_group:
                ${ user.upload_group.name | h }
            %else:
                <i>(None)</i>
            %endif
        </td>
    </tr>
</table>

<h2>Detailed group membership information</h2>

<table>
    <tr>
        <th>Group name</th>
        <th>Group ID</th>
        <th>Group administrator?</th>
        <th>May upload?</th>
        <th>May register devices?</th>
        <th>May use webviewer?</th>
        <th>View all pts when unfiltered?</th>
        <th>May dump?</th>
        <th>May run reports?</th>
        <th>May add notes?</th>
        %if req.user.superuser or req.user.authorized_as_groupadmin:
            <th>Edit</th>
        %endif
    </tr>
    %for ugm in sorted(list(user.user_group_memberships), key=lambda ugm: ugm.group.name):
        <tr>
            <td>${ ugm.group.name | h }</td>
            <td>${ ugm.group_id }</td>
            <td ${ ('class="important"' if ugm.groupadmin else "") }>
                ${ get_yes_no(request, ugm.groupadmin) }
            </td>
            <td>${ get_yes_no(request, ugm.may_upload) }</td>
            <td>${ get_yes_no(request, ugm.may_register_devices) }</td>
            <td>${ get_yes_no(request, ugm.may_use_webviewer) }</td>
            <td>${ get_yes_no(request, ugm.view_all_patients_when_unfiltered) }</td>
            <td>${ get_yes_no(request, ugm.may_dump_data) }</td>
            <td>${ get_yes_no(request, ugm.may_run_reports) }</td>
            <td>${ get_yes_no(request, ugm.may_add_notes) }</td>
            %if req.user.superuser or ugm.group_id in req.user.ids_of_groups_user_is_admin_for:
                <td><a href="${ req.route_url(Routes.EDIT_USER_GROUP_MEMBERSHIP, _query={ViewParam.USER_GROUP_MEMBERSHIP_ID: ugm.id}) }">Edit</a></td>
            %endif
        </tr>
    %endfor
</table>