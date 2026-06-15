# tests/test_workflow.py


class TestWorkflowConditional:
    """测试工作流条件判断函数"""

    def test_should_generate_questions_true(self):
        """测试应该生成题目的情况"""
        from src.workflow import should_generate_questions

        state = {"should_generate_questions": True}

        result = should_generate_questions(state)
        assert result == "generate_questions"

    def test_should_generate_questions_false(self):
        """测试不应该生成题目的情况"""
        from src.workflow import should_generate_questions

        state = {"should_generate_questions": False}

        result = should_generate_questions(state)
        assert result == "end"

    def test_should_generate_questions_missing_key(self):
        """测试缺少should_generate_questions键的情况"""
        from src.workflow import should_generate_questions

        state = {}

        result = should_generate_questions(state)
        assert result == "end"


class TestWorkflowCreation:
    """测试工作流创建"""

    def test_create_resume_screening_workflow(self):
        """测试工作流创建成功"""
        from src.workflow import create_resume_screening_workflow

        workflow = create_resume_screening_workflow()

        # 验证workflow不为None
        assert workflow is not None

        # 验证workflow有invoke方法（编译后的图）
        assert hasattr(workflow, "invoke")
        assert hasattr(workflow, "get_graph")

    def test_workflow_has_correct_nodes(self):
        """测试工作流包含正确的节点"""
        from src.workflow import create_resume_screening_workflow

        workflow = create_resume_screening_workflow()

        # 获取图的节点
        nodes = workflow.get_graph().nodes

        # nodes是一个字典，键是节点名称
        if isinstance(nodes, dict):
            node_names = list(nodes.keys())
        else:
            node_names = list(nodes)

        # 验证包含所有必需的节点
        assert "parse_resume" in node_names
        assert "evaluate_resume" in node_names
        assert "check_threshold" in node_names
        assert "generate_questions" in node_names

    def test_workflow_has_correct_edges(self):
        """测试工作流包含正确的边"""
        from src.workflow import create_resume_screening_workflow

        workflow = create_resume_screening_workflow()

        # 获取图的边
        graph = workflow.get_graph()
        edges = graph.edges

        # 验证边的数量和类型
        assert len(edges) > 0

        # 验证有条件边从check_threshold出发
        conditional_edges = [
            e for e in edges if hasattr(e, "source") and e.source == "check_threshold"
        ]
        assert len(conditional_edges) > 0
