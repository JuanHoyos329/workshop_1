import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from query import (
    kpi_hires_by_technology,
    kpi_hires_by_year,
    kpi_hires_by_seniority,
    kpi_hires_by_country_over_years,
    kpi_hire_rate_by_technology,
    kpi_scores_by_experience,
    get_summary_stats
)

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def clear_screen():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    clear_screen()
    print("=" * 70)
    print("CANDIDATE ANALYSIS DASHBOARD")
    print("=" * 70)
    print("\n📊 Available KPI Visualizations:\n")
    print("1️⃣  Hires by Technology")
    print("2️⃣  Hires by Year")
    print("3️⃣  Hires by Seniority Level")
    print("4️⃣  Hires by Country over Years (USA, Brazil, Colombia, Ecuador)")
    print("5️⃣  Hire Rate Analysis (Top Technologies)")
    print("6️⃣  Experience Analysis")
    print("0️⃣  Exit\n")
    print("=" * 70)

# 1. Hires by Technology
def plot_hires_by_technology():
    df = kpi_hires_by_technology()
    if df is None or df.empty:
        print("No data available")
        return
    df_top10 = df.head(10)
    plt.bar(df_top10['technology_name'], df_top10['total_hires'], color='skyblue', edgecolor='navy')
    plt.xticks(rotation=45, ha='right')
    plt.title("Total Hires by Technology (Top 10)")
    plt.ylabel("Total Hires")
    plt.tight_layout()
    plt.show()

# 2. Hires by Year
def plot_hires_by_year():
    df = kpi_hires_by_year()
    if df is None or df.empty:
        print("No data available")
        return
    plt.plot(df['year'], df['total_hires'], marker='o', linewidth=2, color='green')
    plt.fill_between(df['year'], df['total_hires'], alpha=0.3, color='lightgreen')
    plt.title("Hiring Trend Over Years")
    plt.xlabel("Year")
    plt.ylabel("Total Hires")
    plt.grid(True, alpha=0.3)
    plt.show()

# 3. Hires by Seniority
def plot_hires_by_seniority():
    df = kpi_hires_by_seniority()
    if df is None or df.empty:
        print("No data available")
        return
    colors = plt.cm.Set3(np.linspace(0, 1, len(df)))
    plt.pie(df['total_hires'], labels=df['seniority_name'], autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title("Hire Distribution by Seniority Level")
    plt.show()

# 4. Hires by Country (focus countries only)
def plot_hires_by_country_years():
    df = kpi_hires_by_country_over_years()
    if df is None or df.empty:
        print("No data available")
        return
    focus = ["USA", "Brazil", "Colombia", "Ecuador"]
    df_focus = df[df['country_name'].isin(focus)]
    for country in focus:
        country_data = df_focus[df_focus['country_name'] == country]
        plt.plot(country_data['year'], country_data['total_hires'], marker='o', linewidth=2, label=country)
    plt.title("Hiring Trends by Country")
    plt.xlabel("Year")
    plt.ylabel("Total Hires")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

# 5. Hire Rate Analysis (Top techs only)
def plot_hire_rate_analysis():
    df = kpi_hire_rate_by_technology()
    if df is None or df.empty:
        print("No data available")
        return
    df_top = df.head(8)
    plt.barh(df_top['technology_name'], df_top['hire_rate_percentage'], color='lightcoral')
    plt.xlabel("Hire Rate (%)")
    plt.title("Top Technologies by Hire Rate")
    plt.tight_layout()
    plt.show()

# 6. Experience Analysis
def plot_experience_analysis():
    df = kpi_scores_by_experience()
    if df is None or df.empty:
        print("No data available")
        return
    plt.bar(df['range_label'], df['hire_rate_percentage'], color='gold')
    plt.xticks(rotation=45)
    plt.title("Hire Rate by Experience Range")
    plt.ylabel("Hire Rate (%)")
    plt.tight_layout()
    plt.show()

def run_visualization_dashboard():
    while True:
        show_menu()
        choice = input("👉 Select an option (0-6): ").strip()
        if choice == '0':
            print("\n👋 Thank you for using the Candidate Analysis Dashboard!")
            break
        elif choice == '1':
            plot_hires_by_technology()
        elif choice == '2':
            plot_hires_by_year()
        elif choice == '3':
            plot_hires_by_seniority()
        elif choice == '4':
            plot_hires_by_country_years()
        elif choice == '5':
            plot_hire_rate_analysis()
        elif choice == '6':
            plot_experience_analysis()
        else:
            print("❌ Invalid option.")
        if choice != '0':
            input("\n⏳ Press Enter to return to menu...")

if __name__ == "__main__":
    print("🚀 Starting Candidate Analysis Dashboard...")
    try:
        run_visualization_dashboard()
    except KeyboardInterrupt:
        print("\n👋 Dashboard terminated by user.")