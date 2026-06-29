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

purchase_mode = st.sidebar.radio(
    "구매 채널 모드 선택",
    ["온라인 단일 채널 구매", "복합채널/복합도서 구매"],
    key="purchase_mode"
)

p_cnt = st.session_state.purchase_counter

if purchase_mode == "온라인 단일 채널 구매":
    # 업로드 방식 선택
    p_single_type = st.sidebar.radio("업로드 방식", ["텍스트 파일 업로드", "직접 번호 붙여넣기"], key=f"p_single_type_{p_cnt}")
    purchase_ids = []
    
    if p_single_type == "텍스트 파일 업로드":
        uploaded_purchase = st.sidebar.file_uploader("구매 고객 txt 업로드 (엔터 구분)", type=["txt"], key=f"purchase_single_file_{p_cnt}")
        if uploaded_purchase:
            lines = uploaded_purchase.read().decode("utf-8").splitlines()
            purchase_ids = [line.strip() for line in lines if line.strip()]
    else:
        text_purchase = st.sidebar.text_area("회원번호 입력 (엔터로 구분)", key=f"purchase_single_text_{p_cnt}", height=150)
        if text_purchase:
            purchase_ids = [line.strip() for line in text_purchase.splitlines() if line.strip()]
            
    if purchase_ids:
        new_purchase_df = pd.DataFrame({"고객번호": purchase_ids, "구매채널": "온라인"})
        st.session_state.purchase_data = new_purchase_df.drop_duplicates(subset=["고객번호"]).reset_index(drop=True)
        st.sidebar.success(f"온라인 단일 채널 {len(purchase_ids)}명 로드 완료")

else:  # 복합채널/복합도서 구매
    p_multi_type = st.sidebar.radio("업로드 방식", ["텍스트 파일 업로드", "직접 번호 붙여넣기"], key=f"p_multi_type_{p_cnt}")
    purchase_ids = []
    
    if p_multi_type == "텍스트 파일 업로드":
        uploaded_purchase = st.sidebar.file_uploader("구매 고객 txt 업로드 (엔터 구분)", type=["txt"], key=f"purchase_multi_file_{p_cnt}")
        if uploaded_purchase:
            lines = uploaded_purchase.read().decode("utf-8").splitlines()
            purchase_ids = [line.strip() for line in lines if line.strip()]
    else:
        text_purchase = st.sidebar.text_area("회원번호 입력 (엔터로 구분)", key=f"purchase_multi_text_{p_cnt}", height=150)
        if text_purchase:
            purchase_ids = [line.strip() for line in text_purchase.splitlines() if line.strip()]
            
    channel_input = st.sidebar.text_input("업로드한 파일의 세그먼트명 입력", key=f"channel_input_{p_cnt}")
    
    if st.sidebar.button("구매 데이터 등록"):
        if purchase_ids and channel_input:
            new_purchase_df = pd.DataFrame({"고객번호": purchase_ids, "구매채널": channel_input})
            st.session_state.purchase_data = pd.concat([st.session_state.purchase_data, new_purchase_df]).drop_duplicates(subset=["고객번호"], keep="last").reset_index(drop=True)
            st.session_state.purchase_counter += 1
            st.rerun()
        else:
            st.sidebar.error("데이터(파일/텍스트)를 입력하고 세그먼트명을 입력해주세요.")

st.sidebar.markdown("---")

# 2. 발송 고객 데이터 업로드 영역
st.sidebar.subheader("2. 발송 고객 데이터 추가")

s_cnt = st.session_state.sms_counter
s_type = st.sidebar.radio("업로드 방식", ["텍스트 파일 업로드", "직접 번호 붙여넣기"], key=f"s_type_{s_cnt}")
sms_ids = []

if s_type == "텍스트 파일 업로드":
    uploaded_sms = st.sidebar.file_uploader("발송 고객 txt 업로드 (엔터 구분)", type=["txt"], key=f"sms_upload_file_{s_cnt}")
    if uploaded_sms:
        lines = uploaded_sms.read().decode("utf-8").splitlines()
        sms_ids = [line.strip() for line in lines if line.strip()]
else:
    text_sms = st.sidebar.text_area("회원번호 입력 (엔터로 구분)", key=f"sms_upload_text_{s_cnt}", height=150)
    if text_sms:
        sms_ids = [line.strip() for line in text_sms.splitlines() if line.strip()]

segment_input = st.sidebar.text_input("업로드한 파일의 세그먼트명 입력", key=f"segment_input_{s_cnt}")

if st.sidebar.button("발송 데이터 등록"):
    if sms_ids and segment_input:
        new_sms_df = pd.DataFrame({"고객번호": sms_ids, "세그먼트": segment_input})
        st.session_state.sms_data = pd.concat([st.session_state.sms_data, new_sms_df]).drop_duplicates(subset=["고객번호"], keep="last").reset_index(drop=True)
        st.session_state.sms_counter += 1
        st.rerun()
    else:
        st.sidebar.error("데이터(파일/텍스트)를 입력하고 세그먼트명을 입력해주세요.")

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
        s_summary_table = pd.concat([s_total, s_counts], ignore_index=True)
        
        s_table_col, s_del_col = st.columns([4, 1])
        
        with s_table_col:
            st.markdown("**[세그먼트별 요약]**")
            st.dataframe(s_summary_table, use_container_width=True, hide_index=True)
            
        with s_del_col:
            st.markdown("**[세그먼트 삭제]**")
            current_segments = s_counts["세그먼트"].tolist()
            if current_segments:
                del_segment = st.selectbox("삭제할 세그먼트", options=current_segments, key="del_seg_select", label_visibility="collapsed")
                if st.button("선택 삭제", key="del_seg_btn", use_container_width=True):
                    st.session_state.sms_data = st.session_state.sms_data[st.session_state.sms_data["세그먼트"] != del_segment].reset_index(drop=True)
                    st.rerun()
            else:
                st.caption("삭제할 세그먼트 없음")
                
        st.divider()
        
        with st.expander("▶ 발송 고객 상세 데이터 (상위 5개 미리보기)", expanded=False):
            st.dataframe(
                st.session_state.sms_data.head(5),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("발송 고객 파일을 업로드해주세요.")

# ==========================================
# 메인 화면 하단: [분석 결과] CRM 결과 통합 분석
# ==========================================
if not st.session_state.purchase_data.empty and not st.session_state.sms_data.empty:
    st.header("📈 CRM 결과 분석")
    
    df_sms = st.session_state.sms_data.copy()
    df_purchase = st.session_state.purchase_data.copy()
    
    df_sms["고객번호"] = df_sms["고객번호"].astype(str).str.strip()
    df_purchase["고객번호"] = df_purchase["고객번호"].astype(str).str.strip()
    df_purchase["구매채널"] = df_purchase["구매채널"].astype(str).str.strip()
    
    unique_channels = sorted(df_purchase["구매채널"].unique().tolist())
    selected_channels = unique_channels.copy()
    
    if len(unique_channels) >= 2:
        st.markdown("**🌐 구매 채널 필터 선택**")
        cols = st.columns(len(unique_channels))
        selected_channels = []
        for i, channel in enumerate(unique_channels):
            with cols[i]:
                if st.checkbox(channel, value=True, key=f"chk_{channel}"):
                    selected_channels.append(channel)
        st.divider()

    df_purchase_filtered = df_purchase[df_purchase["구매채널"].isin(selected_channels)]
    df_matched = pd.merge(df_sms, df_purchase_filtered, on="고객번호", how="inner")
    
    st.subheader("(1) 문자메시지 발송 고객 중 상품 구매 현황")
    total_sms_cnt = len(df_sms["고객번호"].unique())
    total_purchase_cnt = len(df_matched["고객번호"].unique())
    conversion_rate = (total_purchase_cnt / total_sms_cnt * 100) if total_sms_cnt > 0 else 0
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="총 문자 발송 고객 수", value=f"{total_sms_cnt:,} 명")
    with kpi2:
        st.metric(label="문자 발송 후 구매 고객 수", value=f"{total_purchase_cnt:,} 명")
    with kpi3:
        st.metric(label="전체 구매 전환율 (CVR)", value=f"{conversion_rate:.2f} %")
        
    st.divider()

    st.subheader("(2) 세그먼트별 상세 분석 결과")
    
    sms_by_seg = df_sms.groupby("세그먼트")["고객번호"].nunique().reset_index(name="발송고객수")
    pure_by_seg = df_matched.groupby("세그먼트")["고객번호"].nunique().reset_index(name="구매고객수")
    
    seg_summary = pd.merge(sms_by_seg, pure_by_seg, on="세그먼트", how="left").fillna(0)
    seg_summary["구매고객수"] = seg_summary["구매고객수"].astype(int)
    
    seg_summary["구매 전환율"] = (seg_summary["구매고객수"] / seg_summary["발송고객수"] * 100).round(2).map("{:.2f} %".format)
    
    total_sms_sum = seg_summary["발송고객수"].sum()
    total_pure_sum = seg_summary["구매고객수"].sum()
    total_cvr = (total_pure_sum / total_sms_sum * 100) if total_sms_sum > 0 else 0
    
    df_total_row = pd.DataFrame([{
        "세그먼트": "합계",
        "발송고객수": total_sms_sum,
        "구매고객수": total_pure_sum,
        "구매 전환율": f"{total_cvr:.2f} %"
    }])
    
    seg_final_table = pd.concat([df_total_row, seg_summary], ignore_index=True)
    st.dataframe(seg_final_table, use_container_width=True, hide_index=True)
    
    st.divider()
    
    with st.expander("▶ 현재 필터 기준 구매 고객 명단 보기", expanded=False):
        if not df_matched.empty:
            st.dataframe(
                df_matched[["고객번호", "세그먼트", "구매채널"]].drop_duplicates().reset_index(drop=True), 
                use_container_width=True
            )
            
            csv = df_matched[["고객번호", "세그먼트", "구매채널"]].drop_duplicates().to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 구매 매칭 고객 명단 다운로드 (CSV)",
                data=csv,
                file_name="sms_purchased_filtered.csv",
                mime="text/csv"
            )
        else:
            st.warning("선택된 조건에 매칭되는 구매 데이터가 없습니다.")
