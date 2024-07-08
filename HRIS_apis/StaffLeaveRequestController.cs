using System;
using System.Collections.Generic;
using System.Data;
using System.Data.Entity;
using System.Linq;
using System.Net;
using System.Web;
using System.Web.Mvc;
using SMS.Web.Models;
using SMS.Web.Logical_Class;
using SMS.Web.ViewModel;
using System.IO;
using SMS.Web.CustomModels;
using System.Threading.Tasks;
using SMS.Web.Models.Enum;
using SMS.Web.CustomModels.Student;
using System.Data.SqlClient;

namespace SMS.Web.Controllers
{
    public class StaffLeaveRequestController : BaseController
    {
        public JsonResult GetStaffDetails(int Staff_ID)
        {
            LeaveRequestViewModel obj = new LeaveRequestViewModel();
            var StaffDetail = db.StaffInfoes.Where(x => x.IsActive == true && x.Staff_ID == Staff_ID).ToList();
            if (StaffDetail.Count > 0)
            {
                obj.studentName = StaffDetail[0].S_Name;
                if (StaffDetail[0].S_FName == null)
                {
                    obj.FatherName = "None";
                }
                else
                {
                    obj.FatherName = StaffDetail[0].S_FName;
                }
            }
            return Json(obj, JsonRequestBehavior.AllowGet);
        }
        [HttpGet]
        public int UniqueDateFromCheck(int StaffID, DateTime? FromDate, DateTime? ToDate)
        {
            var campusId = this.GetCampusIdSelected();
            if (db.StaffLeaveRequest.Where(x => x.status && x.CampusId==campusId).ToList().Where(x => x.StaffId == StaffID && x.FromDate <= FromDate && x.ToDate >= FromDate).Count() > 0)
            {
                return 0;
            }
            if (FromDate != null && ToDate != null)
            {
                if (db.StaffLeaveRequest.Where(x => x.status && x.CampusId == campusId).ToList().Where(x => x.StaffId == StaffID && x.FromDate >= FromDate && x.ToDate <= FromDate).Count() > 0)
                {
                    return 2;
                }
                else
                {
                    return 1;
                }
            }
            return 1;
        }
        [HttpGet]
        public int UniqueDateToCheck(int StaffID, DateTime? FromDate, DateTime? ToDate)
        {
            if (db.StaffLeaveRequest.Where(x => x.status).ToList().Where(x => x.StaffId == StaffID && x.FromDate <= ToDate && x.ToDate >= ToDate).Count() > 0)
            {
                return 0;
            }
            if (FromDate != null && ToDate != null)
            {
                if (db.StaffLeaveRequest.Where(x => x.status).ToList().Where(x => x.StaffId == StaffID && x.FromDate >= FromDate && x.ToDate <= ToDate).Count() > 0)
                {
                    return 2;
                }
                else
                {
                    return 1;
                }
            }
            return 1;
        }
        [HttpGet]
        public ActionResult CheckPresentDetailOnLeave(int StaffID, DateTime FromDate, DateTime ToDate)
        {
            bool someValue;
            var getEmployeeCode = db.StaffAttendances.Where(x => x.staff_Id == StaffID && x.CreateDate >= FromDate.Date && x.atd_status_Id == 1).ToList();
            if (getEmployeeCode.Count > 0)
            {
                someValue = true;
            }
            else
            {
                someValue = false;
            }
            return Json(new { fileError = someValue }, JsonRequestBehavior.AllowGet);
        }
        [HttpGet]
        public int showCheckMaternityPaternityDetail(int StaffID, DateTime FromDate, DateTime ToDate,int LeaveTypeId)
        {
            //(EndDate - StartDate).TotalDays
            if ((LeaveTypeId == 5 || LeaveTypeId == 6) && ((FromDate-DateTime.Today).TotalDays < 30))
            {
                return 0;
            }
            else
            {
                return 1;
            }     
            
        }
        // For Annual Leave

        [HttpGet]
        public int showAnnualDetail(int StaffID, DateTime FromDate, DateTime ToDate, int LeaveTypeId)
        {
            //(EndDate - StartDate).TotalDays
            if (LeaveTypeId == 3  && (FromDate - DateTime.Today).TotalDays < 10)
            {
                return 0;
            }
            else
            {
                return 1;
            }

        }


        //[SMS]
        // GET: /LeaveRequest/
        public ActionResult Index()
        {
            ViewBag.ERROR = TempData["ERROR"] as string;

            //if (usertypeId != (int)Models.Enum.UserType.Parent && usertypeId != (int)Models.Enum.UserType.Student)
                return View(GetLoginStaffsLeaves());

            //return View(GetStaffsLeaves());

        }

        private List<StaffLeaveRequestViewModel> GetStaffsLeaves()
        {
            var campusId = this.GetCampusIdSelected();

            return db.StaffLeaveRequest.Where(x => x.status && x.CampusId == campusId).Select(y => new StaffLeaveRequestViewModel()
            {
                Id = y.Id,
                StaffId = y.StaffId,
                staffName = y.StaffInfo.S_Name,
                FatherName = y.StaffInfo.S_FName,
                FromDate = y.FromDate,
                ToDate = y.ToDate,
                Reason = y.Reason,
                Remarks = y.Remarks,
                LeaveStatusId = y.LeaveStatusId,
                LeaveStatus = y.LeaveStatus.LeaveStatusName,
                LeaveType=y.LeaveType.LeaveTypeName
            }).ToList();
        }

        private List<StaffLeaveRequestViewModel> GetLoginStaffsLeaves()
        {
            var campusId = this.GetCampusIdSelected();
            var userId = this.UserId();
            var userEmail = db.USERS.Find(userId).EMail;
            var StaffId = Convert.ToInt32(Session["StaffId"]);

            return db.StaffLeaveRequest.Where(x => x.status && x.CampusId == campusId && x.StaffId == StaffId).Select(y => new StaffLeaveRequestViewModel()
            {
                Id = y.Id,
                StaffId = y.StaffId,
                staffName = y.StaffInfo.S_Name,
                FatherName = y.StaffInfo.S_FName,
                FromDate = y.FromDate,
                ToDate = y.ToDate,
                Reason = y.Reason,
                Remarks = y.Remarks,
                LeaveStatusId = y.LeaveStatusId,
                LeaveStatus = y.LeaveStatus.LeaveStatusName,
                LeaveType=y.LeaveType.LeaveTypeName

            }).ToList();
        }

        // GET: /LeaveRequest/Create
        //[SMS]
        public async Task<ActionResult> Create()
        {
            try
            {
                ViewBag.ERROR = TempData["ERROR"] as string;

                var academicYear = this.ActiveAcademicYear();
                //var userId = this.UserId();
                var StaffId = Convert.ToInt32(Session["StaffId"]);
                if (StaffId == 0)
                {
                    return RedirectToAction("Index", "Unauthorised");
                }
                //var userTypeId = Convert.ToInt32(Session[SessionName.UserTypeId]);
                //var userEmail = db.USERS.Find(userId).EMail;

                //if (userTypeId != (int)Models.Enum.UserType.Parent && userTypeId != (int)Models.Enum.UserType.Student)
                //{
                //    ViewBag.StaffID = new SelectList(GetStaffs(), "Id", "Name");
                //    return View();
                //}
                var StaffSalaryInfo = db.Salaries.Where(s => s.EmployeeId == StaffId && s.IsActive).SingleOrDefault();
                ViewBag.RemainingCasualLeaves = StaffSalaryInfo.RemainingCasualLeaves;
                ViewBag.RemainingSickLeaves = StaffSalaryInfo.RemainingSickLeaves;
                ViewBag.RemainingAnnualLeaves = StaffSalaryInfo.RemainingAnnualLeaves;
                ViewBag.LeaveTypeId = new SelectList(db.LeaveTypes.Where(s => s.Id != 5 && s.Id != 4 && s.Id != 7).ToList(), "Id", "LeaveTypeName");
                //ViewBag.LeaveTypeId= new SelectList(db.LeaveTypes.ToList(), "Id", "LeaveTypeName");
                //var staff = await db.StaffInfoes.SingleAsync(s => s.S_Email == userEmail);
                var staff = await db.StaffInfoes.SingleAsync(s => s.Staff_ID == StaffId);
                if (staff.S_Gender == 2)
                    ViewBag.LeaveTypeId = new SelectList(db.LeaveTypes.Where(s => s.Id != 6 && s.Id != 4 && s.Id != 7).ToList(), "Id", "LeaveTypeName");
                return View("StaffCreate", new StaffLeaveRequestViewModel(staff));
            }
            catch
            {
                TempData["ERROR"] = "The leave quota has not been created, please create it from the staff edit section. If you encounter any issues, please try again later.";
                return RedirectToAction("Index");
            }
            
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<ActionResult> Create(StaffLeaveRequestViewModel leaveRequestVM)
        {
            try
            {
                // Check Present In Selected Dates
                var CheckAttendance = db.StaffAttendanceTemp.Where(s => s.staff_Id == leaveRequestVM.StaffId && s.time_In != null).Where(s => DbFunctions.TruncateTime(s.CreateDate) >= DbFunctions.TruncateTime(leaveRequestVM.FromDate) && DbFunctions.TruncateTime(s.CreateDate) <= DbFunctions.TruncateTime(leaveRequestVM.ToDate))
                    .Select(a => new { CreateDate = a.CreateDate }).FirstOrDefault();
                if (CheckAttendance != null)
                {
                    TempData["ERROR"] = "Your leave request for between(" + leaveRequestVM.FromDate.ToString("dd-MMM-yyyy") + ") to (" + leaveRequestVM.ToDate.ToString("dd-MMM-yyyy") + ") has not been approved. You were marked as Present in system on that day(" + CheckAttendance.CreateDate.ToString("dd-MMM-yyyy") + ").";
                    return RedirectToAction("Create", "StaffLeaveRequest");
                }

                //Check Duplicate leave In Selected Dates
                var checkduplicateleave = db.StaffLeaveRequest.Where(s => s.status && s.StaffId == leaveRequestVM.StaffId && s.LeaveStatusId != 2).Where(s => (DbFunctions.TruncateTime(s.FromDate) >= DbFunctions.TruncateTime(leaveRequestVM.FromDate) && DbFunctions.TruncateTime(s.FromDate) <= DbFunctions.TruncateTime(leaveRequestVM.ToDate))
                || (DbFunctions.TruncateTime(s.ToDate) >= DbFunctions.TruncateTime(leaveRequestVM.FromDate) && DbFunctions.TruncateTime(s.ToDate) <= DbFunctions.TruncateTime(leaveRequestVM.ToDate))).FirstOrDefault();
                if (checkduplicateleave != null)
                {
                    TempData["ERROR"] = "Your leave request, which is scheduled for the period between (" + leaveRequestVM.FromDate.ToString("dd-MMM-yyyy") + ") to (" + leaveRequestVM.ToDate.ToString("dd-MMM-yyyy") + ") has not been approved. This is because you already have an existing " + checkduplicateleave.LeaveType.LeaveTypeName + " scheduled between (" + checkduplicateleave.FromDate.ToString("dd-MMM-yyyy") + ") to (" + checkduplicateleave.ToDate.ToString("dd-MMM-yyyy") + ").";
                    return RedirectToAction("Create", "StaffLeaveRequest");
                }

                var Month = db.AENcalendars.Where(s => DbFunctions.TruncateTime(s.StartDate) <= DbFunctions.TruncateTime(leaveRequestVM.FromDate) && DbFunctions.TruncateTime(s.EndDate) >= DbFunctions.TruncateTime(leaveRequestVM.ToDate)).FirstOrDefault();
                var academicYear = this.ActiveAcademicYear();
                var Leave = (leaveRequestVM.ToDate - leaveRequestVM.FromDate).TotalDays + 1;
                var Current_academicYear = db.AcademicYears.Where(s => s.academic_year_Id == academicYear).SingleOrDefault();
                var CheckRemainingLeave = db.Salaries.Where(s => s.EmployeeId == leaveRequestVM.StaffId && s.IsActive).SingleOrDefault();

                // Check Reason is not null
                if (leaveRequestVM.Reason == null)
                {
                    TempData["ERROR"] = "A reason is required.";
                    return RedirectToAction("Create", "StaffLeaveRequest");
                }
                // For Paternity & Maternity CHeck once in a year
                if (leaveRequestVM.LeaveTypeId == 5 || leaveRequestVM.LeaveTypeId == 6)
                {
                    var checkleave = db.StaffLeaveRequest.Where(x => x.status).ToList().Where(x => x.CreateDate.Day >= 1 && x.CreateDate.Day <= 31 && ((x.CreateDate.Year >= Current_academicYear.StartDate.Year && x.CreateDate.Month >= 8) || (x.CreateDate.Year <= Current_academicYear.EndDate.Year && x.CreateDate.Month <= 7)) && x.LeaveTypeId == leaveRequestVM.LeaveTypeId && x.LeaveStatusId != 2).Where(s => s.StaffId == leaveRequestVM.StaffId).Count();
                    if (checkleave > 0)
                    {
                        TempData["ERROR"] = "For this particular type, you may apply only once a year " + db.LeaveTypes.Where(s => s.Id == leaveRequestVM.LeaveTypeId).FirstOrDefault().LeaveTypeName + ".";
                        return RedirectToAction("Create", "StaffLeaveRequest");
                    }
                }
                //  Check ToDate is not greater than FromDate
                if (leaveRequestVM.FromDate > leaveRequestVM.ToDate)
                {
                    TempData["ERROR"] = "The To Date must be later than the From Date.";
                    return RedirectToAction("Create", "StaffLeaveRequest");
                }

                // For Casual Leave
                if (leaveRequestVM.LeaveTypeId == 1)
                {
                    var CasualLeave = 0;
                    if (Month != null)
                    {
                        CasualLeave = db.StaffLeaveRequest.Where(x => x.status).ToList().Where(x => x.StaffId == leaveRequestVM.StaffId && ((x.FromDate.Day >= Month.StartDate.Day && x.FromDate.ToString("MMMM") == Month.Month && x.FromDate.Year == Month.StartDate.Year) || (x.ToDate.Day <= Month.EndDate.Day && x.ToDate.ToString("MMMM") == Month.Month && x.ToDate.Year == Month.EndDate.Year)) && x.LeaveTypeId == leaveRequestVM.LeaveTypeId && x.LeaveStatusId != 2).Count();
                    }
                    else
                    {
                        CasualLeave = db.StaffLeaveRequest.Where(x => x.status).ToList().Where(x => x.StaffId == leaveRequestVM.StaffId && ((x.FromDate.Month == leaveRequestVM.FromDate.Month && x.FromDate.Year == leaveRequestVM.FromDate.Year) || (x.ToDate.Month == leaveRequestVM.ToDate.Month && x.ToDate.Year == leaveRequestVM.ToDate.Year)) && x.LeaveTypeId == leaveRequestVM.LeaveTypeId && x.LeaveStatusId != 2).Count();
                    }
                    
                    if (Leave != 1)
                    {
                        TempData["ERROR"] = "The allocation for casual leave is limited to one day per month.";
                        return RedirectToAction("Create", "StaffLeaveRequest");
                    }
                    else if (CheckRemainingLeave.RemainingCasualLeaves < Leave)
                    {
                        TempData["ERROR"] = "You cannot apply for more leave than what remains available.This is because your remaining casual leave is " + CheckRemainingLeave.RemainingCasualLeaves + ".";
                        return RedirectToAction("Create", "StaffLeaveRequest");
                    }
                    else if (CasualLeave > 0)
                    {
                        TempData["ERROR"] = "Already one Casual Leave Exist in Selected month.";
                        return RedirectToAction("Create", "StaffLeaveRequest");
                    }
                }
                // For Sick And Annual Leave
                else if (leaveRequestVM.LeaveTypeId == 2 || leaveRequestVM.LeaveTypeId == 3)
                {
                    if (CheckRemainingLeave.RemainingSickLeaves < Leave && leaveRequestVM.LeaveTypeId == 2)
                    {
                        TempData["ERROR"] = "You cannot apply for more leave than what remains available. This is because your remaining sick leave is " + CheckRemainingLeave.RemainingSickLeaves + ".";
                        return RedirectToAction("Create", "StaffLeaveRequest");
                    }
                    else if (CheckRemainingLeave.RemainingAnnualLeaves < Leave && leaveRequestVM.LeaveTypeId == 3)
                    {
                        TempData["ERROR"] = "You cannot apply for more leave than what remains available. This is because your remaining annual leave is " + CheckRemainingLeave.RemainingAnnualLeaves + ".";
                        return RedirectToAction("Create", "StaffLeaveRequest");
                    }

                }
                // For Paternity Check more than 3 days
                else if (leaveRequestVM.LeaveTypeId == 6 && Leave > 3)
                {
                    TempData["ERROR"] = "For this type of leave, the maximum allowable duration is 3 days.";
                    return RedirectToAction("Create", "StaffLeaveRequest");
                }
                // For Maternity Check More than 30 days
                else if (leaveRequestVM.LeaveTypeId == 5 && Leave > 30)
                {
                    TempData["ERROR"] = "For this type of leave, the maximum allowable duration is 30 days.";
                    return RedirectToAction("Create", "StaffLeaveRequest");
                }

                if (ModelState.IsValid)
                {
                    string path = "";
                    if (leaveRequestVM.File != null && leaveRequestVM.File.ContentLength > 0)
                    {
                        try
                        {
                            path = Path.Combine(Server.MapPath("~/Files/Leaves"),
                                                       Path.GetFileName(leaveRequestVM.StaffId + "_" + leaveRequestVM.File.FileName));
                            if (System.IO.File.Exists(path))
                                System.IO.File.Delete(path);

                            leaveRequestVM.File.SaveAs(path);
                        }
                        catch (Exception ex)
                        {
                            ViewBag.Message = "ERROR:" + ex.Message.ToString();
                        }
                    }

                    if (leaveRequestVM.File != null)
                        leaveRequestVM.LeaveApplicationPath = leaveRequestVM.StaffId + "_" + leaveRequestVM.File.FileName;

                    db.StaffLeaveRequest.Add(new StaffLeaveRequest(leaveRequestVM, academicYear));
                    db.SaveChanges();
                    StaffLeaveDateRangeEntry(leaveRequestVM.FromDate, leaveRequestVM.ToDate);
                    return RedirectToAction("Index");
                }

                var userId = this.UserId();
                var userEmail = db.USERS.Find(userId).EMail;
                var StaffId = Convert.ToInt32(Session["StaffId"]);
            
                var StaffSalaryInfo = db.Salaries.Where(s => s.EmployeeId == StaffId && s.IsActive).SingleOrDefault();
                ViewBag.RemainingCasualLeaves = StaffSalaryInfo.RemainingCasualLeaves;
                ViewBag.RemainingSickLeaves = StaffSalaryInfo.RemainingSickLeaves;
                ViewBag.RemainingAnnualLeaves = StaffSalaryInfo.RemainingAnnualLeaves;
                //ViewBag.LeaveTypeId = new SelectList(db.LeaveTypes.ToList(), "Id", "LeaveTypeName");
                ViewBag.LeaveTypeId = new SelectList(db.LeaveTypes.Where(s => s.Id != 5).ToList(), "Id", "LeaveTypeName");
                //var staff = await db.StaffInfoes.SingleAsync(s => s.S_Email == userEmail);
                var staff = await db.StaffInfoes.SingleAsync(s => s.Staff_ID == StaffId);
                if (staff.S_Gender == 2)
                    ViewBag.LeaveTypeId = new SelectList(db.LeaveTypes.Where(s => s.Id != 6).ToList(), "Id", "LeaveTypeName");
                return View("StaffCreate", new StaffLeaveRequestViewModel(staff));
            }
            catch
            {
                return RedirectToAction("Index");
            }

        }
        public void StaffLeaveDateRangeEntry(DateTime From, DateTime To)
        {
            db.Database.ExecuteSqlCommand("EXEC sp_StaffLeaveDateRangeEntry @From, @To",
                new SqlParameter("@From", From),
                new SqlParameter("@To", To));
        }
        private List<StudentSecondaryCustomModel> GetStaffs()
        {
            return db.StaffInfoes.Where(x => x.IsActive == true).OrderBy(x => x.Staff_ID).Select(
             x => new StudentSecondaryCustomModel
             {
                 Id = x.Staff_ID,
                 Name = x.S_Name
             }).ToList();
        }

        //[SMS]
        public ActionResult Edit(int? id)
        {
            var leaveRequest = db.StaffLeaveRequest.Where(x => x.Id == id && x.status).Select(y => new StaffLeaveRequestViewModel()
            {
                Id = y.Id,
                StaffId = y.StaffId,
                LeaveStatusId = y.LeaveStatusId,
                FatherName = y.StaffInfo.S_FName,
                FromDate = y.FromDate,
                ToDate = y.ToDate,
                Reason = y.Reason,
                Remarks = y.Remarks,
                LeaveApplicationPath = y.LeaveApplicationPath,
                LeaveStatus = y.LeaveStatus.LeaveStatusName,
                LeaveTypeId=y.LeaveTypeId,
                staffName=y.StaffInfo.S_Name,
            }).FirstOrDefault();
            //if (leaveRequest.LeaveStatusId == (int)LeaveStatusName.Pending)
            //{
                //var userTypeId = Convert.ToInt32(Session[SessionName.UserTypeId]);
                //if (userTypeId != (int)Models.Enum.UserType.Parent && userTypeId != (int)Models.Enum.UserType.Student)
                //    return View(leaveRequest);
                ViewBag.LeaveTypeId = new SelectList(db.LeaveTypes.ToList(), "Id", "LeaveTypeName");
                return View("StaffEdit",leaveRequest);
            //}
            
            //return RedirectToAction("Index");
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult Edit(StaffLeaveRequestViewModel leaverequestVM)
        {
            if (ModelState.IsValid)
            {
                string path = "";
                if (leaverequestVM.File != null && leaverequestVM.File.ContentLength > 0)
                {
                    try
                    {
                        path = Path.Combine(Server.MapPath("~/Files/Leaves"),
                                                   Path.GetFileName(leaverequestVM.StaffId + "_" + leaverequestVM.File.FileName));
                        if (System.IO.File.Exists(path))
                        {
                            System.IO.File.Delete(path);
                        }
                        leaverequestVM.File.SaveAs(path);
                    }
                    catch (Exception ex)
                    {
                        ViewBag.Message = "ERROR:" + ex.Message.ToString();
                    }
                }
                if (leaverequestVM.File != null)
                {
                    leaverequestVM.LeaveApplicationPath = leaverequestVM.StaffId + "_" + leaverequestVM.File.FileName;

                }
                StaffLeaveRequest leaverequest = db.StaffLeaveRequest.Find(leaverequestVM.Id);
                //if (leaverequest.LeaveStatusId != 2)
                //{
                //    return View(leaverequestVM);
                //}
                leaverequest.FromDate = leaverequestVM.FromDate;
                leaverequest.ToDate = leaverequestVM.ToDate;
                leaverequest.Reason = leaverequestVM.Reason;
                leaverequest.LeaveApplicationPath = leaverequestVM.LeaveApplicationPath;
                leaverequest.LeaveTypeId = leaverequestVM.LeaveTypeId;
                db.Entry(leaverequest).State = EntityState.Modified;
                db.SaveChanges();

                return RedirectToAction("Index");
            }

            //var userTypeId = Convert.ToInt32(Session[SessionName.UserTypeId]);
            //if (userTypeId != (int)Models.Enum.UserType.Parent && userTypeId != (int)Models.Enum.UserType.Student)
            //    return View(leaverequestVM);
            ViewBag.LeaveTypeId = new SelectList(db.LeaveTypes.ToList(), "Id", "LeaveTypeName");
            return View("StaffEdit", leaverequestVM);
        }

        [HttpGet]
        public PartialViewResult DetailAction(int Id)
        {
            var leaveRequest = db.StaffLeaveRequest.Where(x => x.Id == Id && x.status).Select(y => new StaffLeaveRequestViewModel()
            {
                Id = y.Id,
                StaffId = y.StaffId,
                staffName = y.StaffInfo.S_Name,
                FatherName = y.StaffInfo.S_FName,
                FromDate = y.FromDate,
                ToDate = y.ToDate,
                Reason = y.Reason,
                Remarks = y.Remarks,
                LeaveStatus = y.LeaveStatus.LeaveStatusName,
                LeaveType=y.LeaveType.LeaveTypeName
            }).FirstOrDefault();
            return PartialView("_Detail", leaveRequest);
        }

        //[SMS]
        [HttpPost]
        public JsonResult DeleteAction(int Id)
        {
            ErrorViewModel obj = new ErrorViewModel();
            StaffLeaveRequest leavRequest = db.StaffLeaveRequest.Find(Id);
            //if (leavRequest == null || leavRequest.LeaveStatusId != 2)
            //{
            //    obj.ErrorValue = 2;
            //    return Json(obj, JsonRequestBehavior.AllowGet);
            //}
            leavRequest.status = false;
            db.Entry(leavRequest).State = EntityState.Modified;
            db.SaveChanges();
            obj.ErrorValue = 0;
            return Json(obj, JsonRequestBehavior.AllowGet);
        }

        [HttpPost]
        public ActionResult CheckDuplicateLeave(int StaffID, DateTime FromDate, DateTime ToDate, long IsEdit)
        {
            bool someValue;
            List<StaffLeaveRequest> RequestSubmission = (List<StaffLeaveRequest>)db.StaffLeaveRequest.Where(u => u.StaffId == StaffID
                && u.status == true &&
             ((u.FromDate <= FromDate &&
             u.ToDate >= FromDate) ||
             (u.FromDate <= ToDate &&
             u.ToDate >= ToDate) ||
             (u.FromDate >= FromDate &&
             u.ToDate <= ToDate))).ToList();
            if (IsEdit == 0)
            {

            }
            else
            {
                RequestSubmission = RequestSubmission.Where(x => x.Id != IsEdit).ToList();
            }
            if (RequestSubmission.Count == 0)
            {
                someValue = false;
            }
            else { someValue = true; }
            return Json(new { fileError = someValue });
        }

        public JsonResult StaffUpdatedLeaveStatus()
        {
            var StaffId = Convert.ToInt32(Session["StaffId"]);
            var campusId = this.GetCampusIdSelected();
            if (db.StaffLeaveRequest.Where(s => s.CampusId == campusId && s.StaffId == StaffId && s.status == true).Count()>0)
            {
                var staffMaxleave = db.StaffLeaveRequest.Where(s => s.CampusId == campusId && s.StaffId == StaffId && s.status == true).Max(s => s.Id);
                var Maxleavestatus = db.StaffLeaveRequest.Where(a => a.Id == staffMaxleave).Select(z => z.LeaveStatusId).SingleOrDefault();
                return Json(Maxleavestatus, JsonRequestBehavior.AllowGet);
            }

            else
            {
                return Json(0, JsonRequestBehavior.AllowGet);

            }
            
        }

        public ActionResult Popupleavequota(int id)
        {
            //var leaves = db.Salaries.Where(a=>a.EmployeeId == id).Select(x => new SelectList { })

            List<StaffLeaveQuotaViewModel> staffLeaveQuotaViewModels = new List<StaffLeaveQuotaViewModel>();

            staffLeaveQuotaViewModels = db.Salaries.Where(a => a.EmployeeId == id).Select(q => new StaffLeaveQuotaViewModel
            {
                StaffId = q.EmployeeId,
                StaffName = db.StaffInfoes.FirstOrDefault(s => s.Staff_ID == q.EmployeeId).S_Name,
                CasualLeaves = q.RemainingCasualLeaves,
                SickLeaves = q.RemainingSickLeaves,
                AnnualLeaves = q.RemainingAnnualLeaves,
            }).ToList();

            
            ViewBag.StaffId = id;
            ViewBag.StaffName = db.StaffInfoes.FirstOrDefault(s => s.Staff_ID == id).S_Name;


            return PartialView("_Leavequota", staffLeaveQuotaViewModels);
        }
        public ActionResult LeaveUpdate(int StaffId,DateTime fromDate, DateTime toDate)
        {
            ViewBag.StaffId = StaffId;
            ViewBag.fromDate = fromDate;
            ViewBag.toDate = toDate;
            ViewBag.LeaveTypeId = new SelectList(db.LeaveTypes.Where(s => s.Id == 2 || s.Id == 3).ToList(), "Id", "LeaveTypeName");
            return PartialView("_LeaveUpdate");
        }
        [HttpPost]
        public JsonResult LeaveUpdatePost(int Status, int StaffId, DateTime fromDate, DateTime toDate)
        {
            var UserId = this.UserId();
            string status = "";
            var staff = db.StaffInfoes.Find(StaffId);
            var salaryId = db.Salaries.Where(s => s.EmployeeId == StaffId && s.IsActive).SingleOrDefault();

            if (Status == 2) // Sick Leave
            {
                var StaffLeave = db.StaffLeaveRequest.Where(s => s.status && s.LeaveTypeId == 3 && s.LeaveStatusId == 1 && s.StaffId == StaffId).Where(s => DbFunctions.TruncateTime(s.FromDate) >= fromDate.Date && DbFunctions.TruncateTime(s.FromDate) <= toDate.Date ||
                DbFunctions.TruncateTime(s.ToDate) >= fromDate.Date && DbFunctions.TruncateTime(s.ToDate) <= toDate.Date).ToList();
                int leavecount = 0;
                foreach(var leave in StaffLeave)
                {
                    var CheckHRMarkDayOff = db.MarkDayOffHRs.Where(a => a.status && a.CampusIds == (staff.IsAEN == 0 ? staff.CampusId : 11)).Where(s => DbFunctions.TruncateTime(s.Date) >= DbFunctions.TruncateTime(leave.FromDate) && DbFunctions.TruncateTime(s.Date) <= DbFunctions.TruncateTime(leave.ToDate)).Count();
                    var CheckDepMarkDayOff = db.MarkDayOffDeps.Where(a => a.status && a.Staff_Id == StaffId).Where(s => DbFunctions.TruncateTime(s.Date) >= DbFunctions.TruncateTime(leave.FromDate) && DbFunctions.TruncateTime(s.Date) <= DbFunctions.TruncateTime(leave.ToDate)).Count();
                    var DaysCount = (leave.ToDate - leave.FromDate).TotalDays + 1 - CheckHRMarkDayOff - CheckDepMarkDayOff;
                    leavecount = (int)(leavecount + DaysCount);
                }
                if (salaryId.RemainingSickLeaves >= leavecount)
                {
                    foreach(var leaveType in StaffLeave)
                    {
                        leaveType.LeaveTypeId = 2;
                        db.Entry(leaveType).State = EntityState.Modified;
                        db.SaveChanges();
                    }
                    salaryId.RemainingSickLeaves = (int)(salaryId.RemainingSickLeaves - leavecount);
                    salaryId.RemainingAnnualLeaves = (int)(salaryId.RemainingAnnualLeaves + leavecount);
                    db.Entry(salaryId).State = EntityState.Modified;
                    db.SaveChanges();
                }
                else
                {
                    status = "You cannot update Sick for more leave than what remains available. This is because remaining sick leave is " + salaryId.RemainingSickLeaves + ".";
                }
                
            }
            if (Status == 3) // Annual Leave
            {
                var StaffLeave = db.StaffLeaveRequest.Where(s => s.status && s.LeaveTypeId == 2 && s.LeaveStatusId == 1 && s.StaffId == StaffId).Where(s => DbFunctions.TruncateTime(s.FromDate) >= fromDate.Date && DbFunctions.TruncateTime(s.FromDate) <= toDate.Date ||
                DbFunctions.TruncateTime(s.ToDate) >= fromDate.Date && DbFunctions.TruncateTime(s.ToDate) <= toDate.Date).ToList();
                int leavecount = 0;
                foreach (var leave in StaffLeave)
                {
                    var CheckHRMarkDayOff = db.MarkDayOffHRs.Where(a => a.status && a.CampusIds == (staff.IsAEN == 0 ? staff.CampusId : 11)).Where(s => DbFunctions.TruncateTime(s.Date) >= DbFunctions.TruncateTime(leave.FromDate) && DbFunctions.TruncateTime(s.Date) <= DbFunctions.TruncateTime(leave.ToDate)).Count();
                    var CheckDepMarkDayOff = db.MarkDayOffDeps.Where(a => a.status && a.Staff_Id == StaffId).Where(s => DbFunctions.TruncateTime(s.Date) >= DbFunctions.TruncateTime(leave.FromDate) && DbFunctions.TruncateTime(s.Date) <= DbFunctions.TruncateTime(leave.ToDate)).Count();
                    var DaysCount = (leave.ToDate - leave.FromDate).TotalDays + 1 - CheckHRMarkDayOff - CheckDepMarkDayOff;
                    leavecount = (int)(leavecount + DaysCount);
                }
                if (salaryId.RemainingAnnualLeaves >= leavecount)
                {
                    foreach (var leaveType in StaffLeave)
                    {
                        leaveType.LeaveTypeId = 3;
                        db.Entry(leaveType).State = EntityState.Modified;
                        db.SaveChanges();
                    }
                    salaryId.RemainingSickLeaves = (int)(salaryId.RemainingSickLeaves + leavecount);
                    salaryId.RemainingAnnualLeaves = (int)(salaryId.RemainingAnnualLeaves - leavecount);
                    db.Entry(salaryId).State = EntityState.Modified;
                    db.SaveChanges();
                }
                else
                {
                    status = "You cannot update Annual for more leave than what remains available. This is because remaining Annual leave is " + salaryId.RemainingAnnualLeaves + ".";
                }

            }



            return Json(new { status = status }, JsonRequestBehavior.AllowGet);
        }
    }
}
