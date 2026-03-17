# A/B testing
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint, confint_proportions_2indep
from statsmodels.stats.power import NormalIndPower
import matplotlib.pyplot as plt

# Visualization
#import matplotlib.pyplot as plt
#import seaborn as sns
#import matplotlib.ticker as ticker
#from matplotlib.patches import Patch
import plotly.graph_objects as go

# --- Helper Functions ---
def calculate_cohens_h(p_test, p_control):
    return 2 * (np.arcsin(np.sqrt(p_test)) - np.arcsin(np.sqrt(p_control)))
  
  

def classify_h(h):
    val = abs(h)
    if val < 0.2: return "Negligible"
    elif val < 0.5: return "Small"
    elif val < 0.8: return "Medium"
    else: return "Large"

def calculate_mde(n, baseline_rate, alpha=0.05, power=0.8):
    """Calculates the Minimum Detectable Effect (relative) for a given N and baseline."""
    analysis = NormalIndPower()
    # Solve for effect size (Cohen's h)
    try:
        h_mde = analysis.solve_power(effect_size=None, nobs1=n, alpha=alpha, power=power, ratio=1.0)
        # Convert Cohen's h back to a proportion p2
        # h = 2 * (asin(sqrt(p2)) - asin(sqrt(p1))) -> p2 = sin(h/2 + asin(sqrt(p1)))^2
        p2 = np.sin(h_mde/2 + np.arcsin(np.sqrt(baseline_rate)))**2
        absolute_mde = p2 - baseline_rate
        relative_mde = absolute_mde / baseline_rate
        return absolute_mde, relative_mde
    except:
        return 0, 0 
  
  
  

st.set_page_config(page_title="A/B Conversion Intelligence"
                   ,page_icon="🎯"
                   ,layout="wide"
                   ,initial_sidebar_state="expanded"
                   )

# --- Custom Styling ---
def inject_custom_css():
    st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');

    /* Global */
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Background Animation/Gradient - Subtle */
    .stApp {
        background: radial-gradient(circle at top left, #141c2f 0%, #0b0f19 50%, #05080e 100%);
    }

    /* Top Title Style */
    .lux-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 600;
        background: linear-gradient(45deg, #d4af37, #f3e5ab, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 0px 4px 20px rgba(212, 175, 55, 0.2);
    }
    
    .lux-subtitle {
        color: #94A3B8; 
        font-size: 1.1rem; 
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    /* Metrics / Cards Glassmorphism */
    div[data-testid="stMetric"] {
        background: rgba(20, 28, 47, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.4s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: rgba(212, 175, 55, 0.5);
        box-shadow: 0 12px 40px 0 rgba(212, 175, 55, 0.15);
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 600;
        color: #E2E8F0;
    }
    
    /* Sidebar restyling */
    [data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(212, 175, 55, 0.1);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #d4af37 0%, #b5952f 100%);
        color: #05080e !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4);
        background: linear-gradient(135deg, #f3e5ab 0%, #d4af37 100%);
    }

    /* Fancy subheaders */
    h3 {
        color: #d4af37 !important;
        font-weight: 400 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 1.1rem !important;
        margin-top: 2rem !important;
    }

    /* Success / Info / Warning messages */
    div[data-testid="stAlert"] {
        background: rgba(20, 28, 47, 0.8) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid #d4af37;
        color: #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

st.markdown("<div class='lux-title'>🎯 A/B Conversion Intelligence</div>", unsafe_allow_html=True)

st.markdown("""
<div class='lux-subtitle'>
This app analyzes binary data (e.g., clicks, signups). It automatically detects whether to use 
<b style='color:#d4af37;'>Parametric (Z-test)</b> or <b style='color:#d4af37;'>Non-Parametric (Fisher's Exact)</b> methods based on sample sizes.
</div>
""", unsafe_allow_html=True)


#file = st.sidebar.file_uploader("Upload Conversion Data (csv): Ensure no missing data & deduplicated")
st.sidebar.markdown("<h2 style='text-align: center; color: #D4AF37;'>Data Configuration</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 0.9em; color: #888;'>Upload your dataset to begin</p>", unsafe_allow_html=True)
st.sidebar.divider()

sample_data = st.sidebar.checkbox('Use sample data.')

#st.sidebar.header("1. Upload Data")
#uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

uploaded_file = None

if sample_data:
        uploaded_file = 'sample_data.csv'
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    is_csv = uploaded_file.endswith('.csv') if isinstance(uploaded_file, str) else uploaded_file.name.endswith('.csv')
    df = pd.read_csv(uploaded_file) if is_csv else pd.read_excel(uploaded_file)
    
    st.markdown("---")
    prev_col, sum_col = st.columns(2)
    with prev_col:
        st.subheader("Data Preview")
        st.dataframe(df.head(), use_container_width=True)
    with sum_col:
        st.subheader("Data Summary")
        st.dataframe(df.describe(include='all').T, use_container_width=True)
        #st.write("**Note:** Any missing values in the group or outcome columns will be ignored in the analysis.")
    #st.markdown("---")


    # group col
    group_col = st.sidebar.selectbox('Group Column',list(df.columns))
    df_clean = df.dropna(subset=[group_col])
 
     # Treatment: AB col only 2 values!
    test = st.sidebar.selectbox('Treatment Group',df_clean[group_col].unique())
    
    groups = sorted(df_clean[group_col].unique())
        
    if len(groups) == 2:
        # Control Group
        control = st.sidebar.selectbox('Control Group',[i for i in df_clean[group_col].unique() if test not in i ])
                                                                                
        # conversion col
        outcome_col = st.sidebar.selectbox('Conversion Column',list(df_clean.columns))
        # success col (true or false, 1 or 0)
        success_val = st.sidebar.selectbox("Success Value", df_clean[outcome_col].unique())
    
        df_clean = df_clean.dropna(subset=[outcome_col])

        perform_ab_test = st.sidebar.button("Perform A/B Testing")
    
    
    
        if perform_ab_test:
            st.markdown("---")

            # 1. Statistics
            test_data = df_clean[df_clean[group_col] == test][outcome_col]
            control_data = df_clean[df_clean[group_col] == control][outcome_col]
            
            n1, s1 = len(test_data), len(test_data[test_data == success_val])
            n2, s2 = len(control_data), len(control_data[control_data == success_val])
            r1, r2 = s1/n1, s2/n2
            
            table = pd.DataFrame(
                                {
                                    "Converted": [s1, s2],
                                    "Total": [n1, n2],
                                    "% Converted": [f"{r1*100:.2f}%", f"{r2*100:.2f}%"],
                                },
                                index=pd.Index([test, control]),
                                )
            
            st.subheader("Conversion Summary")
            st.dataframe(table, use_container_width=False)
            st.write("**Note:** Any missing values in the group or outcome columns will be ignored in the analysis.")
            st.markdown("---")





            st.markdown("""### Perform AB Testing:""")
            
            # 2. Adaptive Testing Logic
            use_non_parametric = any(val < 5 for val in [s1, n1-s1, s2, n2-s2])
            if use_non_parametric:
                _, p_val = stats.fisher_exact([[s1, n1-s1], [s2, n2-s2]])
                method = "Fisher's Exact (Non-Parametric)"
            else:
                _, p_val = proportions_ztest([s1, s2], [n1, n2])
                method = "Z-test (Parametric)"

            # 3. CIs and Effect Size
            ci1_low, ci1_high = proportion_confint(s1, n1, alpha=0.05, method='wilson')
            ci2_low, ci2_high = proportion_confint(s2, n2, alpha=0.05, method='wilson')
            
            ci_diff_low, ci_diff_high = confint_proportions_2indep( s1  # successes in Test group
                                                                  , n1 # total in Test group
                                                                  , s2 # successes in Control group
                                                                  , n2 # total in Control group
                                                                  , method='newcombe')
            h_stat = calculate_cohens_h(r1, r2)
            
            # 4. MDE & Power Calculation
            abs_mde, rel_mde = calculate_mde(n1, r1)
            
            analysis = NormalIndPower()
            try:
                curr_power = analysis.solve_power(effect_size=abs(h_stat) if abs(h_stat) > 0.001 else 0.001, 
                                                  nobs1=n1
                                                  ,ratio=n2/n1
                                                  ,alpha=0.05
                                                  ,alternative='larger'
                                                  )
            except:
                curr_power = 0.0
                
                
            # --- DISPLAY ---
            st.subheader(f"Analysis Method: {method}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(f"Rate: {test}", f"{r1:.2%}", help=f"95% CI: [{ci1_low:.2%}, {ci1_high:.2%}]")
            col2.metric(f"Rate: {control}", f"{r2:.2%}", help=f"95% CI: [{ci2_low:.2%}, {ci2_high:.2%}]")
    
            lift = (r1-r2)/r2
            lift_delta = lift - rel_mde
            
            col3.metric("Observed Lift", f"{lift:.2%}", delta=f"{lift_delta:.2%}")
            col4.metric("Statistical MDE", f"{rel_mde:.2%}", help="This is the smallest relative lift this test was capable of detecting with 80% power.")

            
            
            st.markdown("---")
            
            res_left, res_right = st.columns(2)
            with res_left:
                st.subheader("Statistical Significance")
                if p_val < 0.05:
                    st.success(f"**Significant!** (p = {p_val:.4f})")
                else:
                    st.error(f"**Not Significant** (p = {p_val:.4f})")
                    st.write("The difference observed is likely due to random noise.")
                
                st.write(f"The 95% Confidence Interval for the difference is **[{ci_diff_low:.2%}, {ci_diff_high:.2%}]**.")
                st.caption("If the interval includes 0.00%, the result is typically not significant.")

            with res_right:
                st.subheader("Effect Size & Power Analysis")
                st.write(f"**Effect Size (Cohen's h):** {abs(h_stat):.3f} — _{classify_h(h_stat)} Effect_")
                st.write(f"**Statistical Power:** {curr_power:.1%}")
                st.progress(min(float(curr_power), 1.0))
                
                if abs(lift) < rel_mde and p_val >= 0.05:
                    st.warning(f"Your observed lift ({lift:.2%}) was smaller than your test's MDE ({rel_mde:.2%}). "
                               "This test was 'underpowered' to detect an effect this small.")
                elif p_val < 0.05:
                    st.info("The test had enough power to detect this change.")
                
            st.markdown("##")
            with st.expander("Statistical Hypothesis Testing", expanded=False):
                st.markdown("""
                        Using a statistical hypothesis test at 5% significance level.

                        The hypotheses are formulated as follows:
                        
                        -Null Hypothesis (H₀): The conversion rate in the Test group is equal to the Control group (p_Test - p_Control = 0).

                        -Alternative Hypothesis (H₁): The conversion rate in the Test group is higher than in the Control group (p_Test - p_Control > 0).
                        """
                        )
            

            # --- MDE Planner Visualization ---
            st.markdown("---")
            st.subheader("Sample Size Planning Tool")
            #st.write("How many samples would you need to detect *smaller* effects?")
            st.write("This chart shows how many samples you would need to detect a specific relative lift with 80% power.")
            
            #mde_range = np.linspace(0.01, 0.5, 50) # 1% to 50% relative MDE
            mde_range = np.linspace(0.02, 0.40, 40) # 2% to 40%
            required_n = []
            analysis = NormalIndPower()
            
            for m in mde_range:
                target_p2 = r1 * (1 + m)
                if target_p2 > 1: target_p2 = 0.99
                target_h = calculate_cohens_h(target_p2, r1)
                n = analysis.solve_power(effect_size=abs(target_h), alpha=0.05, power=0.8, ratio=1)
                required_n.append(n)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=mde_range * 100, 
                y=required_n, 
                mode='lines', 
                name='Required Samples', 
                line=dict(color='#d4af37', width=3),
                hovertemplate='MDE: %{x:.2f}%<br>Samples: %{y:.0f}<extra></extra>'
            ))
            fig.add_vline(
                x=rel_mde * 100, 
                line_dash="dash", 
                line_color="#E2E8F0", 
                annotation_text=f'Current MDE ({rel_mde:.1%})', 
                annotation_font=dict(color="#E2E8F0"),
                annotation_position="top right"
            )
            fig.update_layout(
                title="Sample Size vs. Sensitivity (Minimum Detectable Effect)",
                title_font=dict(color="#d4af37", size=16),
                xaxis_title="Relative MDE (%)",
                yaxis_title="Required Samples (per group)",
                hovermode="x unified",
                height=400,
                margin=dict(l=0, r=0, t=50, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(20, 28, 47, 0.4)",
                font=dict(color="#E2E8F0"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
            )
            st.plotly_chart(fig, use_container_width=True)
                
            st.markdown('##')
         

    else:
        st.error("Group column must have exactly 2 unique values.")
else:
    st.info("👈 Upload your data to see the Analysis and MDE Planner.")

