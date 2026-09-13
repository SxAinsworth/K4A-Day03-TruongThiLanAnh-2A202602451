"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND

Đề tài:
Vinmec Healthcare Appointment ReAct Agent

Mã nguồn chứa:
1. Tool Schemas theo chuẩn Native JSON Schema.
2. Mock database bác sĩ và lịch khám.
3. Execution Layer phục vụ MCP Server.
"""

import json
from typing import Dict, Any


# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [

    # --------------------------------------------------------------------------
    # TOOL 1: TÌM BÁC SĨ THEO CHUYÊN KHOA
    # --------------------------------------------------------------------------
    {
        "name": "search_doctors",
        "description": (
            "Tìm danh sách bác sĩ Vinmec theo chuyên khoa mà người dùng "
            "muốn khám, ví dụ: Tim mạch, Da liễu, Nhi."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "specialty": {
                    "type": "string",
                    "description": (
                        "Tên chuyên khoa cần tìm bác sĩ. "
                        "Ví dụ: 'Tim mạch', 'Da liễu', 'Nhi'."
                    )
                }
            },
            "required": ["specialty"]
        }
    },

    # --------------------------------------------------------------------------
    # TOOL 2: TRA CỨU LỊCH BÁC SĨ
    # --------------------------------------------------------------------------
    {
        "name": "get_doctor_schedule",
        "description": (
            "Tra cứu các khung giờ khám còn trống của một bác sĩ Vinmec "
            "trong một ngày cụ thể."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {
                    "type": "string",
                    "description": (
                        "Mã bác sĩ được lấy từ kết quả của tool search_doctors. "
                        "Ví dụ: 'D001'."
                    )
                },
                "date": {
                    "type": "string",
                    "description": (
                        "Ngày cần tra cứu lịch khám, theo định dạng YYYY-MM-DD. "
                        "Ví dụ: '2026-09-14'."
                    )
                }
            },
            "required": [
                "doctor_id",
                "date"
            ]
        }
    },

    # --------------------------------------------------------------------------
    # TOOL 3: ĐẶT LỊCH KHÁM
    # --------------------------------------------------------------------------
    {
        "name": "book_appointment",
        "description": (
            "Đặt lịch khám Vinmec với bác sĩ tại một khung giờ còn trống. "
            "Chỉ sử dụng tool này sau khi đã kiểm tra lịch bác sĩ."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {
                    "type": "string",
                    "description": (
                        "Mã bác sĩ cần đặt lịch. "
                        "Ví dụ: 'D001'."
                    )
                },
                "date": {
                    "type": "string",
                    "description": (
                        "Ngày khám theo định dạng YYYY-MM-DD. "
                        "Ví dụ: '2026-09-14'."
                    )
                },
                "time": {
                    "type": "string",
                    "description": (
                        "Khung giờ khám muốn đặt theo định dạng HH:MM. "
                        "Ví dụ: '15:30'."
                    )
                },
                "patient_name": {
                    "type": "string",
                    "description": (
                        "Họ và tên bệnh nhân đặt lịch. "
                        "Ví dụ: 'Trương Thị Lan Anh'."
                    )
                }
            },
            "required": [
                "doctor_id",
                "date",
                "time",
                "patient_name"
            ]
        }
    }
]


# ==============================================================================
# 2. MOCK DATABASE
# ==============================================================================

MOCK_DOCTORS = {
    "D001": {
        "doctor_id": "D001",
        "name": "BS. Nguyễn Văn An",
        "specialty": "Tim mạch",
        "hospital": "Vinmec",
        "experience_years": 12
    },

    "D002": {
        "doctor_id": "D002",
        "name": "BS. Trần Minh Hà",
        "specialty": "Tim mạch",
        "hospital": "Vinmec",
        "experience_years": 9
    },

    "D003": {
        "doctor_id": "D003",
        "name": "BS. Lê Thu Trang",
        "specialty": "Da liễu",
        "hospital": "Vinmec",
        "experience_years": 8
    },

    "D004": {
        "doctor_id": "D004",
        "name": "BS. Phạm Minh Đức",
        "specialty": "Nhi",
        "hospital": "Vinmec",
        "experience_years": 10
    }
}


MOCK_SCHEDULES = {
    "D001": {
        "2026-09-14": [
            "09:00",
            "10:30",
            "14:00",
            "15:30"
        ],
        "2026-09-15": [
            "08:30",
            "10:00",
            "14:30"
        ]
    },

    "D002": {
        "2026-09-14": [
            "08:30",
            "13:30",
            "16:00"
        ],
        "2026-09-15": [
            "09:00",
            "15:00",
            "16:30"
        ]
    },

    "D003": {
        "2026-09-14": [
            "09:30",
            "11:00",
            "14:30"
        ]
    },

    "D004": {
        "2026-09-14": [
            "08:00",
            "10:00",
            "15:00"
        ]
    }
}


# Lưu các appointment đã tạo trong runtime hiện tại.
MOCK_APPOINTMENTS = []


# ==============================================================================
# 3. EXECUTION LAYER - TASK 2.1
# ==============================================================================

def execute_search_doctors(specialty: str) -> str:
    """
    Tìm bác sĩ Vinmec theo chuyên khoa.
    """

    specialty_normalized = specialty.strip().lower()

    doctors = []

    for doctor in MOCK_DOCTORS.values():

        if doctor["specialty"].lower() == specialty_normalized:
            doctors.append(doctor)

    if doctors:
        return json.dumps(
            {
                "status": "SUCCESS",
                "specialty": specialty,
                "count": len(doctors),
                "doctors": doctors
            },
            ensure_ascii=False
        )

    return json.dumps(
        {
            "status": "NOT_FOUND",
            "specialty": specialty,
            "count": 0,
            "doctors": [],
            "message": (
                f"Không tìm thấy bác sĩ thuộc chuyên khoa '{specialty}'."
            )
        },
        ensure_ascii=False
    )


def execute_get_doctor_schedule(
    doctor_id: str,
    date: str
) -> str:
    """
    Tra cứu lịch khám còn trống của bác sĩ trong một ngày.
    """

    doctor_id = doctor_id.strip().upper()
    date = date.strip()

    doctor = MOCK_DOCTORS.get(doctor_id)

    if not doctor:
        return json.dumps(
            {
                "status": "DOCTOR_NOT_FOUND",
                "message": (
                    f"Không tìm thấy bác sĩ có mã '{doctor_id}'."
                )
            },
            ensure_ascii=False
        )

    doctor_schedules = MOCK_SCHEDULES.get(doctor_id, {})

    available_slots = doctor_schedules.get(date, [])

    if not available_slots:
        return json.dumps(
            {
                "status": "NO_AVAILABLE_SLOT",
                "doctor_id": doctor_id,
                "doctor_name": doctor["name"],
                "specialty": doctor["specialty"],
                "date": date,
                "available_slots": [],
                "message": (
                    f"{doctor['name']} hiện không còn lịch trống "
                    f"trong ngày {date}."
                )
            },
            ensure_ascii=False
        )

    return json.dumps(
        {
            "status": "SUCCESS",
            "doctor_id": doctor_id,
            "doctor_name": doctor["name"],
            "specialty": doctor["specialty"],
            "date": date,
            "available_slots": available_slots
        },
        ensure_ascii=False
    )


def execute_book_appointment(
    doctor_id: str,
    date: str,
    time: str,
    patient_name: str
) -> str:
    """
    Thực thi đặt lịch khám.

    Kiểm tra:
    1. Bác sĩ có tồn tại không.
    2. Ngày có lịch không.
    3. Slot có còn trống không.
    4. Nếu hợp lệ thì tạo booking và xóa slot khỏi lịch trống.
    """

    doctor_id = doctor_id.strip().upper()
    date = date.strip()
    time = time.strip()
    patient_name = patient_name.strip()

    doctor = MOCK_DOCTORS.get(doctor_id)

    # --------------------------------------------------------------------------
    # Không tìm thấy bác sĩ
    # --------------------------------------------------------------------------

    if not doctor:
        return json.dumps(
            {
                "status": "DOCTOR_NOT_FOUND",
                "message": (
                    f"Không tìm thấy bác sĩ có mã '{doctor_id}'."
                )
            },
            ensure_ascii=False
        )

    # --------------------------------------------------------------------------
    # Người dùng chưa cung cấp tên bệnh nhân
    # --------------------------------------------------------------------------

    if not patient_name:
        return json.dumps(
            {
                "status": "INVALID_PATIENT_NAME",
                "message": "Tên bệnh nhân không được để trống."
            },
            ensure_ascii=False
        )

    doctor_schedules = MOCK_SCHEDULES.get(doctor_id, {})

    available_slots = doctor_schedules.get(date, [])

    # --------------------------------------------------------------------------
    # Ngày không còn lịch
    # --------------------------------------------------------------------------

    if not available_slots:
        return json.dumps(
            {
                "status": "NO_AVAILABLE_SLOT",
                "doctor_id": doctor_id,
                "doctor_name": doctor["name"],
                "date": date,
                "available_slots": [],
                "message": (
                    f"{doctor['name']} không còn lịch trống "
                    f"trong ngày {date}."
                )
            },
            ensure_ascii=False
        )

    # --------------------------------------------------------------------------
    # Slot user chọn không tồn tại
    # --------------------------------------------------------------------------

    if time not in available_slots:
        return json.dumps(
            {
                "status": "SLOT_NOT_AVAILABLE",
                "doctor_id": doctor_id,
                "doctor_name": doctor["name"],
                "date": date,
                "requested_time": time,
                "available_slots": available_slots,
                "message": (
                    f"Khung giờ {time} không còn trống. "
                    "Vui lòng chọn một khung giờ khác."
                )
            },
            ensure_ascii=False
        )

    # --------------------------------------------------------------------------
    # Tạo booking
    # --------------------------------------------------------------------------

    booking_id = f"VM-{len(MOCK_APPOINTMENTS) + 1:04d}"

    appointment = {
        "booking_id": booking_id,
        "patient_name": patient_name,
        "doctor_id": doctor_id,
        "doctor_name": doctor["name"],
        "specialty": doctor["specialty"],
        "hospital": doctor["hospital"],
        "date": date,
        "time": time
    }

    MOCK_APPOINTMENTS.append(appointment)

    # Slot đã được đặt thì loại khỏi lịch trống.
    MOCK_SCHEDULES[doctor_id][date].remove(time)

    return json.dumps(
        {
            "status": "SUCCESS",
            "booking_id": booking_id,
            "appointment": appointment,
            "message": (
                f"Đặt lịch thành công cho {patient_name} với "
                f"{doctor['name']} vào lúc {time} ngày {date}."
            )
        },
        ensure_ascii=False
    )


# ==============================================================================
# 4. TOOL ROUTER
# ==============================================================================

TOOL_ROUTER = {
    "search_doctors": execute_search_doctors,
    "get_doctor_schedule": execute_get_doctor_schedule,
    "book_appointment": execute_book_appointment
}


def dispatch_tool_call(
    tool_name: str,
    arguments: Dict[str, Any]
) -> str:
    """
    Hàm trung chuyển thực thi Tool.

    MCP Server gọi hàm này sau khi nhận Native Tool Call từ Agent.
    """

    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)

        except TypeError as e:
            return json.dumps(
                {
                    "status": "INVALID_ARGUMENTS",
                    "error": str(e)
                },
                ensure_ascii=False
            )

        except Exception as e:
            return json.dumps(
                {
                    "status": "EXECUTION_ERROR",
                    "error": str(e)
                },
                ensure_ascii=False
            )

    return json.dumps(
        {
            "status": "UNKNOWN_TOOL",
            "error": f"Tool '{tool_name}' không tồn tại!"
        },
        ensure_ascii=False
    )

# ==============================================================================
# 5. LOCAL CHECK - TASK 2.1
# ==============================================================================

if __name__ == "__main__":

    print(
        f"✅ [TOOLS CHECK]: Đã đăng ký thành công "
        f"{len(TOOLS_SCHEMA)} Native Tools trong TOOLS_SCHEMA!"
    )

    print("\n--- TEST 1: search_doctors ---")

    result = dispatch_tool_call(
        "search_doctors",
        {
            "specialty": "Tim mạch"
        }
    )

    result_json = json.loads(result)

    print(result)

    if result_json.get("status") == "SUCCESS":
        print(
            f"🧪 Kết quả gọi thử search_doctors: "
            f"Status SUCCESS "
            f"({result_json.get('count')} bác sĩ được tìm thấy)"
        )
    else:
        print(
            f"❌ search_doctors test failed: "
            f"{result_json}"
        )