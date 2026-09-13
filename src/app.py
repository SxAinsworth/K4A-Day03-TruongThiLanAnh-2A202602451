"""
🚀 CORE AGENT APPLICATION
DAY 03: CHATBOT VS REACT AGENT

Đề tài:
VINMEC HEALTHCARE APPOINTMENT REACT AGENT

Chức năng:
- So sánh Chatbot Baseline và ReAct Agent
- Native Tool Calling
- MCP Client -> MCP Server
- ReAct Loop: Thought -> Action -> Observation
- Waterfall Trace Log
"""

import json
import os
import sys
import time

from dotenv import load_dotenv


# ==============================================================================
# 0. PATH & ENCODING CONFIG
# ==============================================================================

# Cho phép import các file trong thư mục src/
sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Đảm bảo Terminal Windows hiển thị Unicode/tiếng Việt
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(
            encoding="utf-8"
        )
    except Exception:
        pass


# ==============================================================================
# 1. IMPORT PROJECT MODULES
# ==============================================================================

# Tạm thời giữ tên class MCPAcademicServer để tương thích với template gốc.
# Khi sửa mcp_server.py có thể đổi thành MCPHealthcareServer sau.
from mcp_server import MCPAcademicServer

from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)

from providers import get_llm_provider


# ==============================================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ==============================================================================

load_dotenv()


# ==============================================================================
# 3. LOAD TEST CASES
# ==============================================================================

def load_test_cases():
    """
    Tải danh sách Test Cases từ:

        config/test_cases.json

    Nếu chưa tồn tại thì fallback sang:

        config/test_cases.example.json
    """

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    config_path = os.path.join(
        base_dir,
        "config",
        "test_cases.json"
    )

    if not os.path.exists(config_path):

        example_path = os.path.join(
            base_dir,
            "config",
            "test_cases.example.json"
        )

        if os.path.exists(example_path):

            print(
                "⚠️ [CONFIG NOTICE]: "
                "Chưa thấy file 'config/test_cases.json'."
            )

            print(
                "👉 Đang sử dụng "
                "'config/test_cases.example.json'."
            )

            print(
                "👉 Hãy copy file mẫu thành "
                "'config/test_cases.json' "
                "và viết Test Cases theo đề tài.\n"
            )

            config_path = example_path

        else:

            raise FileNotFoundError(
                "Không tìm thấy "
                "config/test_cases.json "
                "hoặc config/test_cases.example.json"
            )

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==============================================================================
# 4. WATERFALL TRACE
# ==============================================================================

def save_waterfall_trace(trace_data: list):
    """
    Ghi Waterfall Trace Log vào:

        docs/trace_waterfall.json

    Trace dùng làm bằng chứng cho:
        Thought / Decision
        -> Action
        -> Observation
        -> Final Answer
    """

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    docs_dir = os.path.join(
        base_dir,
        "docs"
    )

    os.makedirs(
        docs_dir,
        exist_ok=True
    )

    trace_path = os.path.join(
        docs_dir,
        "trace_waterfall.json"
    )

    with open(
        trace_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            trace_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"📊 [OBSERVABILITY]: "
        f"Đã lưu {len(trace_data)} sự kiện "
        f"Waterfall Trace tại:\n"
        f"   {trace_path}"
    )


# ==============================================================================
# 5. CHATBOT BASELINE
# ==============================================================================

def run_baseline_chatbot(
    user_query: str,
    provider
):
    """
    Chatbot Baseline:

    - Không có Tool
    - Không MCP
    - Chỉ sinh câu trả lời bằng LLM
    """

    print(
        f"\n💬 [CHATBOT BASELINE] "
        f"Câu hỏi: {user_query}"
    )

    response = provider.generate(
        user_query,
        system_prompt=CHATBOT_BASELINE_PROMPT
    )

    print(
        f"🤖 [CHATBOT RESPONSE]:\n"
        f"{response}"
    )


# ==============================================================================
# 6. HELPER: NORMALIZE MCP OBSERVATION
# ==============================================================================

def normalize_observation(
    mcp_result
):
    """
    Chuẩn hóa result trả về từ MCP Server.

    Hỗ trợ trường hợp:

    1. result là dict
    2. result là JSON string
    3. result là raw string
    """

    if not isinstance(
        mcp_result,
        dict
    ):
        return {
            "status": "INVALID_MCP_RESPONSE",
            "data": mcp_result
        }

    observation = mcp_result.get(
        "result",
        {}
    )

    # MCP result có thể là JSON string
    if isinstance(
        observation,
        str
    ):
        try:
            observation = json.loads(
                observation
            )

        except json.JSONDecodeError:

            observation = {
                "status": "RAW_RESPONSE",
                "data": observation
            }

    if observation is None:
        observation = {}

    return observation


# ==============================================================================
# 7. TASK 2.2 - REACT AGENT LOOP
# ==============================================================================

def run_react_agent(
    user_query: str,
    provider,
    mcp_server: MCPAcademicServer
) -> list:
    """
    TASK 2.2
    ========

    Thực thi ReAct Loop:

        User Query
            ↓
        Thought / Decision
            ↓
        Có cần Tool?
          /      \\
       Không      Có
        ↓          ↓
      Final      Action
      Answer        ↓
                 MCP Server
                    ↓
               Observation
                    ↓
             quay lại LLM
                    ↓
               bước tiếp theo

    Agent có thể gọi NHIỀU Tool liên tiếp trước khi đưa ra Final Answer.

    Ví dụ:

        search_doctors
            ↓
        get_doctor_schedule
            ↓
        book_appointment
            ↓
        Final Answer
    """

    print(
        f"\n🤖 [REACT AGENT] "
        f"Câu hỏi: {user_query}"
    )

    step = 0

    trace_logs = []

    final_answer_generated = False

    # Lấy Native Tool Schema từ MCP Server
    tools_list = mcp_server.list_tools()

    # Context được cập nhật sau mỗi Observation.
    #
    # Đây là phần quan trọng giúp Agent thực hiện
    # Multi-step ReAct.
    working_context = user_query


    # ==========================================================================
    # REACT LOOP
    # ==========================================================================

    while step < MAX_ITERATIONS:

        step += 1

        step_start_time = time.time()

        print(
            f"\n--- 🔄 ReAct Loop "
            f"(Step {step}/{MAX_ITERATIONS}) ---"
        )


        # ======================================================================
        # THOUGHT / DECISION
        # ======================================================================

        llm_response = provider.generate_with_tools(
            working_context,
            tools_list,
            system_prompt=REACT_AGENT_SYSTEM_PROMPT
        )

        latency_ms = round(
            (
                time.time()
                - step_start_time
            )
            * 1000,
            2
        )


        thought = llm_response.get(
            "thought",
            "Agent đang xác định hành động tiếp theo."
        )

        print(
            f"🧠 [Thought]: "
            f"{thought}"
        )


        response_type = llm_response.get(
            "type"
        )


        # ======================================================================
        # CASE 1
        # LLM KHÔNG CẦN TOOL -> FINAL ANSWER
        # ======================================================================

        if response_type == "text":

            final_content = llm_response.get(
                "content",
                ""
            )

            print(
                f"🏁 [Final Answer]: "
                f"{final_content}"
            )

            trace_logs.append(
                {
                    "step": step,
                    "query": user_query,
                    "action_type": "FINAL_ANSWER",
                    "thought": thought,
                    "output": final_content,
                    "latency_ms": latency_ms
                }
            )

            final_answer_generated = True

            break


        # ======================================================================
        # CASE 2
        # LLM QUYẾT ĐỊNH GỌI TOOL
        # ======================================================================

        elif response_type == "tool_call":

            tool_name = llm_response.get(
                "tool_name"
            )

            arguments = llm_response.get(
                "arguments",
                {}
            )


            # ==================================================================
            # ACTION
            # ==================================================================

            print(
                f"🛠️ [Action Proposed]: "
                f"{tool_name}({arguments})"
            )


            # ==================================================================
            # MCP CLIENT -> MCP SERVER
            # ==================================================================

            try:

                mcp_result = mcp_server.call_tool(
                    tool_name,
                    arguments
                )

            except Exception as error:

                error_observation = {
                    "status": "MCP_CALL_ERROR",
                    "error": str(error)
                }

                print(
                    "❌ [MCP ERROR]: "
                    f"{error_observation}"
                )

                trace_logs.append(
                    {
                        "step": step,
                        "query": user_query,
                        "action_type": "TOOL_ERROR",
                        "thought": thought,
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "observation": error_observation,
                        "latency_ms": latency_ms
                    }
                )

                break


            # ==================================================================
            # OBSERVATION
            # ==================================================================

            obs_data = normalize_observation(
                mcp_result
            )

            obs_str = json.dumps(
                obs_data,
                ensure_ascii=False
            )

            print(
                "👁️ [Observation từ MCP Server]: "
                f"{obs_str}"
            )


            # ==================================================================
            # SAVE TRACE
            # ==================================================================

            trace_logs.append(
                {
                    "step": step,
                    "query": user_query,
                    "action_type": "TOOL_EXECUTION",
                    "thought": thought,
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "observation": obs_data,
                    "latency_ms": latency_ms
                }
            )


            # ==================================================================
            # ĐƯA OBSERVATION TRỞ LẠI LLM
            #
            # KHÔNG BREAK Ở ĐÂY.
            #
            # Đây là điểm quan trọng nhất của ReAct Loop.
            # ==================================================================

            working_context += (
                "\n\n"
                "==============================\n"
                "OBSERVATION TỪ MCP TOOL\n"
                "==============================\n"
                f"Tool: {tool_name}\n"
                f"Arguments: "
                f"{json.dumps(arguments, ensure_ascii=False)}\n"
                f"Observation: {obs_str}\n"
                "==============================\n"
                "\n"
                "Hãy tiếp tục xử lý yêu cầu ban đầu của người dùng. "
                "Dựa vào Observation vừa nhận được, hãy quyết định:\n"
                "- Có cần gọi thêm Tool hay không.\n"
                "- Nếu cần, hãy chọn Tool tiếp theo phù hợp.\n"
                "- Nếu đã đủ dữ liệu, hãy trả Final Answer.\n"
                "- Không được tự bịa bác sĩ, lịch khám hoặc kết quả đặt lịch.\n"
            )


            # Quay lại đầu while để LLM suy luận tiếp
            continue


        # ======================================================================
        # CASE 3
        # RESPONSE TYPE KHÔNG HỢP LỆ
        # ======================================================================

        else:

            error_message = (
                "LLM Provider trả về response type "
                f"không hợp lệ: {response_type}"
            )

            print(
                f"❌ [REACT ERROR]: "
                f"{error_message}"
            )

            trace_logs.append(
                {
                    "step": step,
                    "query": user_query,
                    "action_type": "ERROR",
                    "thought": thought,
                    "output": error_message,
                    "latency_ms": latency_ms
                }
            )

            break


    # ==========================================================================
    # MAX ITERATIONS SAFETY
    # ==========================================================================

    if (
        not final_answer_generated
        and step >= MAX_ITERATIONS
    ):

        final_message = (
            "Agent đã đạt số vòng xử lý tối đa "
            "nhưng chưa thể hoàn thành yêu cầu."
        )

        print(
            f"⚠️ [MAX ITERATIONS]: "
            f"{final_message}"
        )

        trace_logs.append(
            {
                "step": step + 1,
                "query": user_query,
                "action_type": "MAX_ITERATIONS_REACHED",
                "output": final_message
            }
        )


    return trace_logs


# ==============================================================================
# 8. MAIN APPLICATION
# ==============================================================================

if __name__ == "__main__":

    print(
        "=========================================================="
    )

    print(
        "🏫 VINUNI AI COURSE - DAY 03 LAB"
    )

    print(
        "🤖 CHATBOT VS REACT AGENT"
    )

    print(
        "🏥 TOPIC: VINMEC HEALTHCARE APPOINTMENT AGENT"
    )

    print(
        "=========================================================="
    )


    # ==========================================================================
    # INITIALIZE PROVIDER
    # ==========================================================================

    provider = get_llm_provider()


    # ==========================================================================
    # INITIALIZE MCP SERVER
    #
    # Hiện tại giữ tên class gốc MCPAcademicServer
    # để tránh làm hỏng dependency.
    # ==========================================================================

    mcp_server = MCPAcademicServer()


    print(
        f"🔌 LLM Provider: "
        f"{provider.__class__.__name__}"
    )

    print(
        f"🌐 MCP Server: "
        f"{mcp_server.server_name}\n"
    )


    # ==========================================================================
    # LOAD TEST CASES
    # ==========================================================================

    tests = load_test_cases()

    print(
        f"✅ Đã tải thành công "
        f"{len(tests)} Test Cases thử nghiệm.\n"
    )


    # ==========================================================================
    # INTERACTIVE MODE
    # ==========================================================================

    if "--interactive" in sys.argv:

        print(
            "🎮 [INTERACTIVE MODE] "
            "Trò chuyện trực tiếp với ReAct Agent:"
        )

        print(
            "\n💡 Gợi ý câu hỏi thử nghiệm:"
        )

        print(
            "   1. 'Bạn có thể hỗ trợ tôi những gì "
            "khi đặt lịch khám Vinmec?'"
        )

        print(
            "   2. 'Hãy tìm giúp tôi các bác sĩ "
            "chuyên khoa Tim mạch.'"
        )

        print(
            "   3. 'Bác sĩ D001 có lịch "
            "ngày 14/09/2026 không?'"
        )

        print(
            "   4. 'Hãy đặt lịch khám cho "
            "Trương Thị Lan Anh với bác sĩ D001 "
            "vào lúc 15:30 ngày 14/09/2026.'"
        )

        print(
            "   5. 'Tôi muốn khám Tim mạch "
            "vào lúc 14:00 ngày 14/09/2026, "
            "bác sĩ nào cũng được. "
            "Hãy tìm bác sĩ phù hợp và đặt lịch "
            "cho Trương Thị Lan Anh.'"
        )

        print(
            "\n   Gõ 'exit' hoặc 'quit' "
            "để kết thúc phiên trò chuyện.\n"
        )


        while True:

            try:

                user_input = input(
                    "👤 Người dùng hỏi: "
                ).strip()


                if (
                    not user_input
                    or user_input.lower()
                    in [
                        "exit",
                        "quit"
                    ]
                ):

                    print(
                        "👋 Tạm biệt! "
                        "Kết thúc phiên trò chuyện."
                    )

                    break


                logs = run_react_agent(
                    user_input,
                    provider,
                    mcp_server
                )


                save_waterfall_trace(
                    logs
                )


            except (
                KeyboardInterrupt,
                EOFError
            ):

                print(
                    "\n👋 Đã thoát "
                    "phiên tương tác."
                )

                break


    # ==========================================================================
    # RUN ALL TEST CASES
    # ==========================================================================

    elif "--all" in sys.argv:

        print(
            "🚀 [TEST SUITE MODE] "
            "Kiểm tra toàn bộ Test Cases:"
        )


        completed_count = 0

        todo_count = 0

        all_traces = []


        for tc in tests:

            print(
                "\n=================================================="
            )

            print(
                f"🧪 [{tc['id']}] "
                f"Loại test: {tc['type']} "
                f"(Độ phức tạp: "
                f"{tc['complexity']})"
            )

            print(
                f"📌 Kỳ vọng: "
                f"{tc['expected_behavior']}"
            )


            question = tc[
                "question"
            ].strip()


            # ==============================================================
            # TODO TEST CASE
            # ==============================================================

            if question.startswith(
                "TODO"
            ):

                print(
                    "⏸️ [CHƯA KÍCH HOẠT "
                    "- ĐANG LÀ TODO]:"
                )

                print(
                    f"   {question}"
                )

                print(
                    "   👉 Hãy mở file "
                    "'config/test_cases.json' "
                    "để hoàn thiện Test Case."
                )

                todo_count += 1


            # ==============================================================
            # EXECUTE TEST CASE
            # ==============================================================

            else:

                logs = run_react_agent(
                    question,
                    provider,
                    mcp_server
                )

                all_traces.extend(
                    logs
                )

                completed_count += 1


        # ==================================================================
        # TEST SUMMARY
        # ==================================================================

        print(
            "\n=================================================="
        )

        print(
            "📊 [KẾT QUẢ TEST SUITE]: "
            f"Đã thực thi "
            f"{completed_count}/{len(tests)} "
            "Test Cases | "
            f"{todo_count} Test Cases "
            "đang chờ điền câu hỏi (TODO)"
        )


        if all_traces:

            save_waterfall_trace(
                all_traces
            )


        print(
            "\n💡 Để trò chuyện trực tiếp từng câu:"
        )

        print(
            "   python src/app.py --interactive"
        )


    # ==========================================================================
    # BASELINE MODE
    # ==========================================================================

    elif "--baseline" in sys.argv:

        print(
            "💬 [BASELINE MODE]"
        )

        sample_query = (
            "Tôi muốn tìm bác sĩ Tim mạch "
            "và đặt lịch khám."
        )

        run_baseline_chatbot(
            sample_query,
            provider
        )


    # ==========================================================================
    # DEFAULT MODE
    # ==========================================================================

    else:

        print(
            "ℹ️ HƯỚNG DẪN SỬ DỤNG:"
        )

        print(
            "  1. Chat với ReAct Agent:"
        )

        print(
            "     python src/app.py --interactive"
        )

        print(
            "\n  2. Chạy toàn bộ Test Cases:"
        )

        print(
            "     python src/app.py --all"
        )

        print(
            "\n  3. Chạy Chatbot Baseline:"
        )

        print(
            "     python src/app.py --baseline"
        )


        # ==================================================================
        # DEFAULT DEMO TC02
        # ==================================================================

        if len(tests) >= 2:

            sample_query = tests[1][
                "question"
            ]

            print(
                "\n--- 🏁 DEMO TEST CASE TC02: "
                "TÌM BÁC SĨ THEO CHUYÊN KHOA ---"
            )

            logs = run_react_agent(
                sample_query,
                provider,
                mcp_server
            )

            save_waterfall_trace(
                logs
            )


        print(
            "\n💡 Hãy thử:"
        )

        print(
            "   python src/app.py --interactive"
        )