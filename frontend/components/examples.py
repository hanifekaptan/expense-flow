"""
Example Queries Component
"""
import streamlit as st


EXAMPLE_QUERIES = {
    "student": {
        "title": "🎓 Öğrenci Bütçesi (Haftalık)",
        "query": """starbucks latte 85 TL
migros market alışverişi 280 TL
ders kitabı matematik 450 TL
kampüste öğle yemeği 75 TL
netflix aboneliği 149.99 TL
spotify premium 54.99 TL
uber kampüse gidiş 95 TL
teknosa kulaklık 899 TL
dominos pizza 320 TL"""
    },
    "home": {
        "title": "🏠 Ev Harcamaları (Aylık)",
        "query": """kira ödemesi 8500 TL
doğalgaz faturası 850 TL
elektrik faturası 620 TL
internet + cep telefonu 399 TL
carrefour market 1450 TL
a101 temel gıda 680 TL
temizlik malzemeleri 340 TL
su arıtma cihazı filtre 180 TL
eczane ilaç 420 TL"""
    },
    "tech": {
        "title": "💻 Teknoloji Alışverişi",
        "query": """apple macbook pro m3 16gb 52999 TL
logitech mx master 3s mouse 2499 TL
keychron k2 mekanik klavye 3200 TL
samsung 27 inch monitör 8500 TL
anker usb-c hub 7 port 899 TL
seagate 2tb harici disk 2200 TL
apple magic trackpad 3850 TL
laptop çantası 450 TL"""
    },
    "vacation": {
        "title": "✈️ Tatil Harcamaları (Haftalık)",
        "query": """hilton otel konaklama 3 gece 12500 TL
pegasus uçak bileti gidiş-dönüş 4200 TL
hertz araba kiralama 5 gün 3500 TL
restoran akşam yemeği 1850 TL
müze giriş biletleri 4 kişi 680 TL
plaj kulübü günlük 1200 TL
airport transfer 450 TL
hediyelik eşya 890 TL
deniz bisikleti kiralama 600 TL"""
    }
}


def render_example_queries() -> None:
    """
    Render example query buttons.
    
    When a button is clicked, the example query is stored in session state.
    """
    with st.expander("💡 Örnek Sorgular - Tıklayın"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                EXAMPLE_QUERIES["student"]["title"],
                use_container_width=True
            ):
                st.session_state["example_query"] = EXAMPLE_QUERIES["student"]["query"]
                st.rerun()
            
            if st.button(
                EXAMPLE_QUERIES["home"]["title"],
                use_container_width=True
            ):
                st.session_state["example_query"] = EXAMPLE_QUERIES["home"]["query"]
                st.rerun()
        
        with col2:
            if st.button(
                EXAMPLE_QUERIES["tech"]["title"],
                use_container_width=True
            ):
                st.session_state["example_query"] = EXAMPLE_QUERIES["tech"]["query"]
                st.rerun()
            
            if st.button(
                EXAMPLE_QUERIES["vacation"]["title"],
                use_container_width=True
            ):
                st.session_state["example_query"] = EXAMPLE_QUERIES["vacation"]["query"]
                st.rerun()
