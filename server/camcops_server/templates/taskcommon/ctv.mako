## ctv.mako
## <%page args="tracker: ClinicalTextView, viewtype: str, pdf_landscape: bool"/>

<%!

from cardinal_pythonlib.datetimefunc import format_datetime
from camcops_server.cc_modules.cc_audit import audit
from camcops_server.cc_modules.cc_constants import DateFormat
from camcops_server.cc_modules.cc_pyramid import Routes, ViewArg, ViewParam

%>

<%inherit file="tracker_ctv.mako"/>

<%block name="office_preamble">
    The clinical text view uses only information from tasks that are flagged
    CURRENT.
</%block>

%if not tracker.patient:

    <div class="warning">
        No patient found for tracker.
    </div>

%else:

    <div class="ctv_datelimit_start">
        Start date/time for search: ${ format_datetime(tracker.taskfilter.start_datetime,
                                                       DateFormat.ISO8601_HUMANIZED_TO_MINUTES, default="−∞") }
    </div>

    %for task in tracker.collection.all_tasks:
        <% ctvinfo_list = task.get_clinical_text(request) %>

        ## --------------------------------------------------------------------
        ## Heading
        ## --------------------------------------------------------------------
        <div class="ctv_taskheading">
            ## Creation date/time
            ${ format_datetime(task.get_creation_datetime(),
                               DateFormat.LONG_DATETIME_WITH_DAY) }:
            ## Task name
            ${ task.longname | h }
            %if not ctvinfo_list:
                exists
            %endif
            ## Hyperlinks
            %if viewtype == ViewArg.HTML:
                [<a href="${ req.route_url(
                    Routes.TASK,
                    _query={
                        ViewParam.TABLE_NAME: task.tablename,
                        ViewParam.SERVER_PK: task._pk,
                        ViewParam.VIEWTYPE: ViewArg.HTML,
                    }) }">HTML</a>]
                [<a href="${ req.route_url(
                    Routes.TASK,
                    _query={
                        ViewParam.TABLE_NAME: task.tablename,
                        ViewParam.SERVER_PK: task._pk,
                        ViewParam.VIEWTYPE: ViewArg.PDF,
                    }) }">PDF</a>]
            %endif
            ## Clinician
            %if task.has_clinician and ctvinfo_list:
                <i>(Clinician: ${ task.get_clinician_name() | h })</i>
            %endif
        </div>

        %if ctvinfo_list:
            ## ----------------------------------------------------------------
            ## Warnings, special notes
            ## ----------------------------------------------------------------
            %if (not task._current) or (not task.field_contents_valid()) or task.special_notes:
                <div class="ctv_warnings">
                    %if not task._current:
                        <%include file="task_not_current.mako" args="task=task"/>
                    %endif
                    %if not task.field_contents_valid():
                        <%include file="task_contents_invalid.mako" args="task=task"/>
                    %endif
                    %if task.special_notes:
                        <%include file="special_notes.mako" args="special_notes=task.special_notes, title='TASK SPECIAL NOTES'"/>
                    %endif
                </div>
            %endif

            ## ----------------------------------------------------------------
            ## Content
            ## ----------------------------------------------------------------
            %for ctvinfo in ctvinfo_list:
                %if ctvinfo.heading:
                    <div class="ctv_fieldheading">${ ctvinfo.heading }</div>
                %endif
                %if ctvinfo.subheading:
                    <div class="ctv_fieldsubheading">${ ctvinfo.subheading }</div>
                %endif
                %if ctvinfo.description:
                    <div class="ctv_fielddescription">${ ctvinfo.description }</div>
                %endif
                %if ctvinfo.content:
                    <div class="ctv_fieldcontent">${ ctvinfo.content }</div>
                %endif
            %endfor

            <%
                audit(
                    request,
                    "Clinical text view accessed",
                    table=task.tablename,
                    server_pk=task.get_pk(),
                    patient_server_pk=task.get_patient_server_pk()
                )
            %>
        %endif

    %endfor

    <div class="ctv_datelimit_end">
        End date/time for search: ${ format_datetime(tracker.taskfilter.end_datetime,
                                                     DateFormat.ISO8601_HUMANIZED_TO_MINUTES, default="+∞") }
    </div>
%endif
