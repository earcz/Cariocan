import streamlit as st

def render(conn, user_row):
    st.subheader("Reminders")
    water_on = st.toggle("Water")
    posture_on = st.toggle("Posture")
    js = f"""
    <script>
    const waterOn = {str(water_on).lower()};
    const postureOn = {str(posture_on).lower()};
    function inRange(h, start, end) {{ return h>=start && h<end; }}
    function notify(msg) {{
      if (!('Notification' in window)) return;
      if (Notification.permission !== 'granted') Notification.requestPermission();
      if (Notification.permission === 'granted') new Notification('Carioca', {{ body: msg }});
      try {{ new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg').play(); }} catch(e){{}}
    }}
    function schedule() {{
      const now = new Date(); const h = now.getHours();
      if (waterOn && inRange(h,8,22)) setTimeout(()=>notify("Ceku balım su içtin mi?"), 1000);
      if (postureOn && inRange(h,8,21)) setTimeout(()=>notify("Dik dur eğilme, bu taraftar seninle"), 2000);
      if (waterOn) setInterval(()=>{{ const h=(new Date()).getHours(); if(inRange(h,8,22)) notify("Ceku balım su içtin mi?"); }}, 2*60*60*1000);
      if (postureOn) setInterval(()=>{{ const h=(new Date()).getHours(); if(inRange(h,8,21)) notify("Dik dur eğilme, bu taraftar seninle"); }}, 3*60*60*1000);
    }}
    schedule();
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)
