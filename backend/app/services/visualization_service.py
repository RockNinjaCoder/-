import os
from typing import Dict, List, Optional, Any
from app.core.nlp.chart_recommender import chart_recommender, ChartRecommender
from app.core.db.executor import query_executor


class VisualizationService:
    """
    可视化服务层
    整合图表推荐、配置生成、数据处理
    """

    def __init__(self):
        self.chart_recommender = ChartRecommender()

    def generate_chart_config(
        self,
        data: List[Dict],
        chart_type: str = None,
        title: str = "",
        x_axis_column: str = None,
        y_axis_column: str = None
    ) -> Dict[str, Any]:
        """
        生成图表配置

        Args:
            data: 查询结果数据
            chart_type: 图表类型
            title: 图表标题
            x_axis_column: X 轴列名
            y_axis_column: Y 轴列名

        Returns:
            ECharts 配置字典
        """
        return self.chart_recommender.generate_chart_config(
            data=data,
            chart_type=chart_type,
            title=title,
            x_axis_column=x_axis_column,
            y_axis_column=y_axis_column
        )

    def auto_generate_from_sql(self, sql: str, chart_type: str = None) -> Dict[str, Any]:
        """
        从 SQL 查询自动生成图表配置

        Args:
            sql: SQL 语句
            chart_type: 图表类型（可选）

        Returns:
            包含图表配置和数据的字典
        """
        success, result, data = query_executor.execute_query(sql)

        if not success:
            return {
                "success": False,
                "error": result,
                "chart_config": None,
                "data": None
            }

        if not data or len(data) == 0:
            return {
                "success": True,
                "chart_config": None,
                "data": [],
                "message": "无数据可可视化"
            }

        recommended_chart_type = chart_type or self.chart_recommender.recommend_chart_type(data)

        chart_config = self.chart_recommender.generate_chart_config(
            data=data,
            chart_type=recommended_chart_type,
            title=f"SQL 查询结果 - {recommended_chart_type.upper()}"
        )

        return {
            "success": True,
            "chart_config": chart_config,
            "data": data,
            "recommended_chart_type": recommended_chart_type
        }

    def recommend_chart_type(self, data: List[Dict], user_preference: str = None) -> str:
        """
        推荐图表类型

        Args:
            data: 查询结果数据
            user_preference: 用户偏好

        Returns:
            推荐的图表类型
        """
        return self.chart_recommender.recommend_chart_type(data, user_preference)

    def get_available_chart_types(self) -> List[Dict]:
        """
        获取所有可用的图表类型

        Returns:
            图表类型列表
        """
        return self.chart_recommender.get_available_chart_types()

    def analyze_data_structure(self, data: List[Dict]) -> Dict[str, Any]:
        """
        分析数据结构

        Args:
            data: 查询结果数据

        Returns:
            数据结构分析结果
        """
        return self.chart_recommender.analyze_data_structure(data)

    def get_chart_config_for_visualization(
        self,
        sql: str,
        chart_type: str = None,
        title: str = "",
        x_axis_column: str = None,
        y_axis_column: str = None
    ) -> Dict[str, Any]:
        """
        获取完整的可视化配置

        Args:
            sql: SQL 语句
            chart_type: 图表类型
            title: 图表标题
            x_axis_column: X 轴列名
            y_axis_column: Y 轴列名

        Returns:
            完整的可视化配置
        """
        result = self.auto_generate_from_sql(sql, chart_type)

        if not result["success"]:
            return result

        if result.get("chart_config") is None:
            return result

        if title:
            result["chart_config"]["title"]["text"] = title

        if x_axis_column or y_axis_column:
            result["chart_config"] = self.chart_recommender.generate_chart_config(
                data=result["data"],
                chart_type=result.get("recommended_chart_type", "bar"),
                title=title,
                x_axis_column=x_axis_column,
                y_axis_column=y_axis_column
            )

        return {
            "success": True,
            "chart_config": result["chart_config"],
            "data": result["data"],
            "chart_type": result.get("recommended_chart_type"),
            "data_analysis": self.analyze_data_structure(result["data"])
        }


visualization_service = VisualizationService()