import sanic
from models.report import Report
from models.users import BaseUser
from utilities.users import format_user_name


reports_service = sanic.BluePrint(
    "ReportsService",
    url_prefix="/reports_service"
)


def make_report_json_view(report):
    user = report.user.single()

    json = {
        **report.__properties__,
        "user_name": format_user_name(user)
    }

    return json


@reports_service.post("/create_report")
def create_report(request):
    user_id = request.json["user_id"]
    content = request.json["content"]

    user = BaseUser.nodes.first(user_id=userd_id)
    report = Report(content=content).save()

    report.user.connect(user)

    return sanic.empty()


@reports_service.post("/get_all_reports")
def get_all_reports(request):
    reports = Report.nodes.all()

    json = [
        make_report_json_view(report)
        for report in reports
    ]

    return sanic.json(json)


@reports_service.post("/delete_report")
def delete_report(request):
    report_id = request["report_id"]

    report = Report.nodes.first(report_id=report_id)

    report.delete()

    return sanic.empty()
