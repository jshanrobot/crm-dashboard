import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 고객 CRM 결과 분석 대시보드")

# ==========================================
# 세션 상태(Session State) 초기화
# ==========================================
if "sms_data" not in st.session_state:
    st.session_state.sms_data = pd.DataFrame(columns=["고객번호", "세그먼트"])
if "purchase_data" not in st.session_state:
    st.session_state.purchase_data = pd.DataFrame(columns=["고객번호", "구매채널"])

# 입력창 초기화를 위한 카운터 변수
if "sms_counter" not in st.session_state:
    st.session_state.sms_counter = 0
if "purchase_counter" not in st.session_state:
    st.session_state.purchase_counter = 0

# ==========================================
# 사이드바: 데이터 업로드 및 관리
# ==========================================
st.sidebar.header("📁 데이터 업로드 관리")

# 1. 구매 고객 데이터 업로드 영역
st.sidebar.subheader("1. 구매 고객 데이터")

# 채널 선택 라디오 버튼 (변경사항 1 반영)
purchase_mode = st.sidebar.radio(
    "구매 채널 모드 선택",
    ["온라인 단일 채널 구매", "복합채널/복합도서 구매"],
    key="purchase_mode"
)

p_cnt = st.session_state.purchase_counter

if purchase_mode == "온라인 단일 채널 구매":
    uploaded_purchase = st.sidebar.file_uploader("구매 고객 txt 업로드 (엔터 구분)", type=["txt"], key=f"purchase_single_{p_cnt}")
    
    if uploaded_purchase:
        lines = uploaded_purchase.read().decode("utf-8").splitlines()
        purchase_ids = [line.strip() for line in lines if line.strip()]
        
        # '온라인'으로 자동 분류하여 데이터프레임 생성
        new_purchase_df = pd.DataFrame({"고객번호": purchase_ids, "구매채널": "온라인"})
        
        # 기존 데이터 덮어쓰기 (단일 채널 모드이므로 새로 올릴 때마다 갱신)
        st.session_state.purchase_data = new_purchase_df.drop_duplicates(subset=["고객번호"]).reset_index(drop=True)
        st.sidebar.success(f"온라인 단일 채널 {len(purchase_ids)}명 로드 완료")

else:  # 복합채널/복합도서 구매
    uploaded_purchase = st.sidebar.file_uploader("구매 고객 txt 업로드 (엔터 구분)", type=["txt"], key=f"purchase_multi_{p_cnt}")
    # 변경사항 2 반영
    channel_input = st.sidebar.text_input("업로드한 파일의 세그먼트명 입력", key=f"channel_input_{p_cnt}")
    
    # 변경사항 3 반영
    if st.sidebar.button("구매 데이터 등록"):
        if uploaded_purchase and channel_input:
            lines = uploaded_purchase.read().decode("utf-8").splitlines()
            purchase_ids = [line.strip() for line in lines if line.strip()]
            
            new_purchase_df = pd.DataFrame({"고객번호": purchase_ids, "구매채널": channel_input})
            
            # 기존 데이터와 병합 (중복 제거 시 최근 등록 채널 우선)
            st.session_state.purchase_data = pd.concat([st.session_state.purchase_data, new_purchase_df]).drop_duplicates(subset=["고객번호"], keep="last").reset_index(drop=True)
            
            # 카운터 증가 및 새로고침으로 입력창 초기화
            st.session_state.purchase_counter += 1
            st.rerun()
        else:
            st.sidebar.error("파일을 업로드하고 세그먼트명을 입력해주세요.")

st.sidebar.markdown("---")

# 2. 발송 고객 데이터 업로드 영역
st.sidebar.subheader("2. 발송 고객 데이터 추가")

s_cnt = st.session_state.sms_counter
uploaded_sms = st.sidebar.file_uploader("발송 고객 txt 업로드 (엔터 구분)", type=["txt"], key=f"sms_upload_{s_cnt}")
segment_input = st.sidebar.text_input("업로드한 파일의 세그먼트명 입력", key=f"segment_input_{s_cnt}")

# 변경사항 4 반영
if st.sidebar.button("발송 데이터 등록"):
    if uploaded_sms and segment_input:
        lines = uploaded_sms.read().decode("utf-8").splitlines()
        sms_ids = [line.strip() for line in lines if line.strip()]
        
        new_sms_df = pd.DataFrame({"고객번호": sms_ids, "세그먼트": segment_input})
        st.session_state.sms_data = pd.concat([st.session_state.sms_data, new_sms_df]).drop_duplicates(subset=["고객번호"], keep="last").reset_index(drop=True)
        
        st.session_state.sms_counter += 1
        st.rerun()
    else:
        st.sidebar.error("파일을 업로드하고 세그먼트명을 입력해주세요.")

# ==========================================
# 메인 화면: 데이터 확인 및 수정
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛒 구매 고객 리스트")
    if not st.session_state.purchase_data.empty:
        df_p_summary = st.session_state.purchase_data.copy()
        df_p_summary["구매채널"] = df_p_summary["구매채널"].astype(str).str.strip()
        
        p_counts = df_p_summary.groupby("구매채널")["고객번호"].nunique().reset_index()
        p_counts.columns = ["구매채널", "구매고객수"]
        
        p_total = pd.DataFrame([{"구매채널": "합계", "구매고객수": p_counts["구매고객수"].sum()}])
        p_summary_table = pd.concat([p_total, p_counts], ignore_index=True)
        
        p_table_col, p_del_col = st.columns([4, 1])
        
        with p_table_col:
            st.markdown("**[구매 채널별 요약]**")
            st.dataframe(p_summary_table, use_container_width=True, hide_index=True)
            
        with p_del_col:
            st.markdown("**[채널 삭제]**")
            current_channels = p_counts["구매채널"].tolist()
            if current_channels:
                del_channel = st.selectbox("삭제할 채널", options=current_channels, key="del_ch_select", label_visibility="collapsed")
                if st.button("선택 삭제", key="del_ch_btn", use_container_width=True):
                    st.session_state.purchase_data = st.session_state.purchase_data[st.session_state.purchase_data["구매채널"] != del_channel].reset_index(drop=True)
                    st.rerun()
            else:
                st.caption("삭제할 채널 없음")
                
        st.divider()
        
        with st.expander("▶ 구매 고객 상세 데이터 (상위 5개 미리보기)", expanded=False):
            st.dataframe(
                st.session_state.purchase_data.head(5),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("구매 고객 파일을 업로드해주세요.")

with col2:
    st.subheader("💬 발송 고객 리스트")
    if not st.session_state.sms_data.empty:
        df_s_summary = st.session_state.sms_data.copy()
        df_s_summary["세그먼트"] = df_s_summary["세그먼트"].astype(str).str.strip()
        
        s_counts = df_s_summary.groupby("세그먼트")["고객번호"].nunique().reset_index()
        s_counts.columns = ["세그먼트", "발송고객수"]
        
        s_total = pd.DataFrame([{"세그먼트": "합계", "발송고객수": s_counts["발송고객수"].sum()}])
        s_summary_table = pd.
