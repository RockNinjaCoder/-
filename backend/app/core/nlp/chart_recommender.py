import os
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv

load_dotenv()


class ChartRecommender:
    """
    可视化配置生成器
    根据查询结果数据特征推荐合适的图表类型并生成 ECharts 配置
    """

    CHART_CONFIGS = {
        "line": {
            "type": "line",
            "title": "折线图",
            "description": "适合展示数据随时间变化的趋势",
            "suitable_for": ["时间序列", "趋势分析", "连续数据"]
        },
        "bar": {
            "type": "bar",
            "title": "柱状图",
            "description": "适合比较不同类别之间的数值差异",
            "suitable_for": ["分类对比", "离散数据", "排名分析"]
        },
        "pie": {
            "type": "pie",
            "title": "饼图",
            "description": "适合展示各部分占总体的比例关系",
            "suitable_for": ["占比分析", "比例分布", "百分比展示"]
        },
        "scatter": {
            "type": "scatter",
            "title": "散点图",
            "description": "适合展示两个变量之间的相关性",
            "suitable_for": ["相关性分析", "分布展示", "异常检测"]
        }
    }

    def __init__(self):
        """初始化图表推荐器"""
        self.default_config = {
            "backgroundColor": "transparent",
            "title": {
                "text": "",
                "left": "center",
                "textStyle": {
                    "fontSize": 16,
                    "fontWeight": "normal"
                }
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} ({d}%)"
            },
            "legend": {
                "orient": "horizontal",
                "bottom": 10,
                "type": "scroll"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": []
            },
            "yAxis": {
                "type": "value"
            },
            "series": []
        }

    def analyze_data_structure(self, data: List[Dict]) -> Dict[str, Any]:
        """
        分析数据结构

        Args:
            data: 查询结果数据

        Returns:
            数据结构分析结果
        """
        if not data or len(data) == 0:
            return {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "data_types": {},
                "has_time_column": False,
                "has_numeric_column": False,
                "has_categorical_column": False
            }

        columns = list(data[0].keys())
        data_types = {}
        has_time_column = False
        has_numeric_column = False
        has_categorical_column = False

        time_keywords = ["time", "date", "日期", "时间", "year", "month", "day"]
        numeric_types = ["int", "float", "real", "number", "numeric"]

        for col in columns:
            sample_values = [row.get(col) for row in data[:10] if row.get(col) is not None]

            col_lower = col.lower()
            if any(kw in col_lower for kw in time_keywords):
                has_time_column = True

            numeric_count = 0
            for val in sample_values:
                if isinstance(val, (int, float)):
                    numeric_count += 1
                elif isinstance(val, str):
                    try:
                        float(val)
                        numeric_count += 1
                    except ValueError:
                        pass

            if len(sample_values) > 0 and numeric_count / len(sample_values) > 0.5:
                has_numeric_column = True
                data_types[col] = "numeric"
            else:
                has_categorical_column = True
                data_types[col] = "categorical"

        return {
            "row_count": len(data),
            "column_count": len(columns),
            "columns": columns,
            "data_types": data_types,
            "has_time_column": has_time_column,
            "has_numeric_column": has_numeric_column,
            "has_categorical_column": has_categorical_column
        }

    def recommend_chart_type(self, data: List[Dict], user_preference: str = None) -> str:
        """
        推荐图表类型

        Args:
            data: 查询结果数据
            user_preference: 用户偏好（可选）

        Returns:
            推荐的图表类型
        """
        if user_preference and user_preference in self.CHART_CONFIGS:
            return user_preference

        analysis = self.analyze_data_structure(data)

        if analysis["row_count"] == 0:
            return "bar"

        if analysis["has_time_column"] and analysis["has_numeric_column"]:
            return "line"

        if analysis["column_count"] == 1 and analysis["has_numeric_column"]:
            return "bar"

        if analysis["column_count"] == 2:
            return "scatter"

        numeric_cols = [col for col, dtype in analysis["data_types"].items() if dtype == "numeric"]
        if len(numeric_cols) >= 1:
            return "bar"

        return "pie"

    def generate_chart_config(
        self,
        data: List[Dict],
        chart_type: str = "bar",
        title: str = "",
        x_axis_column: str = None,
        y_axis_column: str = None
    ) -> Dict[str, Any]:
        """
        生成 ECharts 图表配置

        Args:
            data: 查询结果数据
            chart_type: 图表类型
            title: 图表标题
            x_axis_column: X 轴列名
            y_axis_column: Y 轴列名

        Returns:
            ECharts 配置字典
        """
        config = self.default_config.copy()
        config["title"]["text"] = title or f"{chart_type.upper()} Chart"

        if not data or len(data) == 0:
            config["title"]["text"] = "无数据"
            return config

        analysis = self.analyze_data_structure(data)
        columns = analysis["columns"]

        if x_axis_column is None:
            x_axis_column = columns[0] if len(columns) > 0 else "x"
        if y_axis_column is None:
            y_axis_column = columns[-1] if len(columns) > 1 else columns[0]

        if chart_type in ["line", "bar"]:
            x_data = [row.get(x_axis_column, f"Item {i}") for i, row in enumerate(data)]
            y_data = [self._extract_numeric_value(row.get(y_axis_column, 0)) for row in data]

            config["xAxis"] = {
                "type": "category",
                "data": x_data,
                "axisLabel": {
                    "rotate": 30 if len(x_data) > 5 else 0
                }
            }
            config["yAxis"] = {
                "type": "value"
            }
            config["series"] = [{
                "name": y_axis_column,
                "type": chart_type,
                "data": y_data,
                "itemStyle": {
                    "color": "#5470c6" if chart_type == "bar" else "#91d5ff"
                },
                "label": {
                    "show": len(y_data) <= 10,
                    "position": "top"
                }
            }]
            config["grid"]["bottom"] = "20%" if len(x_data) > 5 else "10%"

        elif chart_type == "pie":
            pie_data = []
            for row in data:
                name = row.get(x_axis_column, "Unknown")
                value = self._extract_numeric_value(row.get(y_axis_column, 0))
                pie_data.append({"name": str(name), "value": value})

            config["series"] = [{
                "name": title,
                "type": "pie",
                "radius": ["40%", "70%"],
                "data": pie_data,
                "label": {
                    "formatter": "{b}: {c} ({d}%)"
                }
            }]
            config["legend"]["orient"] = "vertical"
            config["legend"]["left"] = "left"
            config["legend"]["bottom"] = "auto"
            del config["xAxis"]
            del config["yAxis"]
            del config["grid"]

        elif chart_type == "scatter":
            scatter_data = [
                [
                    self._extract_numeric_value(row.get(x_axis_column, 0)),
                    self._extract_numeric_value(row.get(y_axis_column, 0))
                ]
                for row in data
            ]

            config["xAxis"] = {
                "type": "value",
                "name": x_axis_column,
                "splitLine": {"show": True}
            }
            config["yAxis"] = {
                "type": "value",
                "name": y_axis_column,
                "splitLine": {"show": True}
            }
            config["series"] = [{
                "name": "scatter",
                "type": "scatter",
                "symbolSize": 15,
                "data": scatter_data,
                "itemStyle": {
                    "color": "#5470c6"
                }
            }]

        return config

    def _extract_numeric_value(self, value: Any) -> float:
        """
        提取数值

        Args:
            value: 任意类型的值

        Returns:
            数值（如果无法提取则返回 0）
        """
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.replace(",", "").replace("%", ""))
            except ValueError:
                return 0
        return 0

    def get_chart_config_by_data(self, data: List[Dict], chart_type: str = None, **kwargs) -> Dict[str, Any]:
        """
        根据数据获取完整的图表配置

        Args:
            data: 查询结果数据
            chart_type: 图表类型（可选，如果不提供则自动推荐）
            **kwargs: 其他配置参数

        Returns:
            完整的 ECharts 配置
        """
        if chart_type is None:
            chart_type = self.recommend_chart_type(data)

        title = kwargs.get("title", "")
        x_axis_column = kwargs.get("x_axis_column")
        y_axis_column = kwargs.get("y_axis_column")

        return self.generate_chart_config(
            data=data,
            chart_type=chart_type,
            title=title,
            x_axis_column=x_axis_column,
            y_axis_column=y_axis_column
        )

    def get_available_chart_types(self) -> List[Dict]:
        """
        获取所有可用的图表类型

        Returns:
            图表类型列表
        """
        return [
            {"type": key, **value}
            for key, value in self.CHART_CONFIGS.items()
        ]


chart_recommender = ChartRecommender()