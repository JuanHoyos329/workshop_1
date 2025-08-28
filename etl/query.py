from connection import get_connection
import pandas as pd

def execute_query(query, description):
    """Execute a SQL query and return results as DataFrame"""
    try:
        connection = get_connection()
        df = pd.read_sql(query, connection)
        connection.close()
        print(f"✅ {description}: {len(df)} records")
        return df
    except Exception as e:
        print(f"❌ Error executing {description}: {e}")
        return None

# KPI 1: HIRES BY TECHNOLOGY
def kpi_hires_by_technology():
    """Get number of hires by technology"""
    query = """
    SELECT 
        dt.technology_name,
        COUNT(fa.id) as total_applications,
        SUM(fa.hired_flag) as total_hires,
        ROUND((SUM(fa.hired_flag) / COUNT(fa.id)) * 100, 2) as hire_rate_percentage
    FROM Fact_Application fa
    JOIN Dim_Technology dt ON fa.technology_key = dt.technology_key
    GROUP BY dt.technology_name
    ORDER BY total_hires DESC;
    """
    return execute_query(query, "Hires by Technology")

# KPI 2: HIRES BY YEAR
def kpi_hires_by_year():
    """Get number of hires by year"""
    query = """
    SELECT 
        dd.year,
        COUNT(fa.id) as total_applications,
        SUM(fa.hired_flag) as total_hires,
        ROUND((SUM(fa.hired_flag) / COUNT(fa.id)) * 100, 2) as hire_rate_percentage
    FROM Fact_Application fa
    JOIN Dim_Date dd ON fa.date_key = dd.date_key
    GROUP BY dd.year
    ORDER BY dd.year;
    """
    return execute_query(query, "Hires by Year")

# KPI 3: HIRES BY SENIORITY
def kpi_hires_by_seniority():
    """Get number of hires by seniority level"""
    query = """
    SELECT 
        ds.seniority_name,
        COUNT(fa.id) as total_applications,
        SUM(fa.hired_flag) as total_hires,
        ROUND((SUM(fa.hired_flag) / COUNT(fa.id)) * 100, 2) as hire_rate_percentage
    FROM Fact_Application fa
    JOIN Dim_Seniority ds ON fa.seniority_key = ds.seniority_key
    GROUP BY ds.seniority_name
    ORDER BY total_hires DESC;
    """
    return execute_query(query, "Hires by Seniority")

# KPI 4: HIRES BY COUNTRY OVER YEARS (Focus: USA, Brazil, Colombia, Ecuador)
def kpi_hires_by_country_over_years():
    """Get hires by specific countries over years"""
    query = """
    SELECT 
        dc.country_name,
        dd.year,
        COUNT(fa.id) as total_applications,
        SUM(fa.hired_flag) as total_hires,
        ROUND((SUM(fa.hired_flag) / COUNT(fa.id)) * 100, 2) as hire_rate_percentage
    FROM Fact_Application fa
    JOIN Dim_Country dc ON fa.country_key = dc.country_key
    JOIN Dim_Date dd ON fa.date_key = dd.date_key
    WHERE dc.country_name IN ('United States', 'Brazil', 'Colombia', 'Ecuador', 
                              'USA', 'United States of America')
    GROUP BY dc.country_name, dd.year
    ORDER BY dc.country_name, dd.year;
    """
    return execute_query(query, "Hires by Country over Years (Focus Countries)")

# KPI 5: HIRE RATE PERCENTAGE BY TECHNOLOGY (Additional KPI)
def kpi_hire_rate_by_technology():
    """Get detailed hire rate analysis by technology"""
    query = """
    SELECT 
        dt.technology_name,
        COUNT(fa.id) as total_applications,
        SUM(fa.hired_flag) as total_hires,
        COUNT(fa.id) - SUM(fa.hired_flag) as total_rejected,
        ROUND((SUM(fa.hired_flag) / COUNT(fa.id)) * 100, 2) as hire_rate_percentage,
        ROUND(AVG(fa.code_challenge_score), 2) as avg_code_score,
        ROUND(AVG(fa.technical_interview_score), 2) as avg_interview_score
    FROM Fact_Application fa
    JOIN Dim_Technology dt ON fa.technology_key = dt.technology_key
    WHERE fa.code_challenge_score IS NOT NULL 
      AND fa.technical_interview_score IS NOT NULL
    GROUP BY dt.technology_name
    HAVING COUNT(fa.id) >= 10  -- Only technologies with at least 10 applications
    ORDER BY hire_rate_percentage DESC;
    """
    return execute_query(query, "Hire Rate Analysis by Technology")

# KPI 6: AVERAGE SCORES BY EXPERIENCE RANGE (Additional KPI)
def kpi_scores_by_experience():
    """Get average scores and hire rates by experience range"""
    query = """
    SELECT 
        der.range_label,
        der.min_years,
        der.max_years,
        COUNT(fa.id) as total_applications,
        SUM(fa.hired_flag) as total_hires,
        ROUND((SUM(fa.hired_flag) / COUNT(fa.id)) * 100, 2) as hire_rate_percentage,
        ROUND(AVG(fa.code_challenge_score), 2) as avg_code_challenge_score,
        ROUND(AVG(fa.technical_interview_score), 2) as avg_technical_interview_score,
        ROUND(AVG(fa.yoe), 1) as avg_years_of_experience
    FROM Fact_Application fa
    JOIN Dim_ExperienceRange der ON fa.experience_key = der.experience_key
    WHERE fa.code_challenge_score IS NOT NULL 
      AND fa.technical_interview_score IS NOT NULL
    GROUP BY der.range_label, der.min_years, der.max_years
    ORDER BY der.min_years;
    """
    return execute_query(query, "Performance Analysis by Experience Range")

# CONSOLIDATED DASHBOARD DATA
def get_all_kpis():
    """Execute all KPI queries and return results"""
    print("🔹 Executing All KPI Queries...")
    
    kpis = {
        'hires_by_technology': kpi_hires_by_technology(),
        'hires_by_year': kpi_hires_by_year(),
        'hires_by_seniority': kpi_hires_by_seniority(),
        'hires_by_country_years': kpi_hires_by_country_over_years(),
        'hire_rate_by_technology': kpi_hire_rate_by_technology(),
        'scores_by_experience': kpi_scores_by_experience()
    }
    
    print("✅ All KPI queries completed!")
    return kpis

# SUMMARY STATISTICS
def get_summary_stats():
    """Get overall summary statistics"""
    query = """
    SELECT 
        COUNT(fa.id) as total_applications,
        SUM(fa.hired_flag) as total_hires,
        ROUND((SUM(fa.hired_flag) / COUNT(fa.id)) * 100, 2) as overall_hire_rate,
        COUNT(DISTINCT fa.candidate_key) as unique_candidates,
        COUNT(DISTINCT dt.technology_name) as total_technologies,
        COUNT(DISTINCT dc.country_name) as total_countries,
        COUNT(DISTINCT ds.seniority_name) as total_seniority_levels,
        ROUND(AVG(fa.code_challenge_score), 2) as avg_code_score,
        ROUND(AVG(fa.technical_interview_score), 2) as avg_interview_score,
        MIN(dd.year) as earliest_year,
        MAX(dd.year) as latest_year
    FROM Fact_Application fa
    JOIN Dim_Technology dt ON fa.technology_key = dt.technology_key
    JOIN Dim_Country dc ON fa.country_key = dc.country_key
    JOIN Dim_Seniority ds ON fa.seniority_key = ds.seniority_key
    JOIN Dim_Date dd ON fa.date_key = dd.date_key;
    """
    return execute_query(query, "Overall Summary Statistics")