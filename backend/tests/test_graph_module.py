# 图谱构建模块测试用例
# 测试实体提取器、关系提取器、图谱构建器和存储功能

import unittest
import json
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.modules.graph.extractor import LLMEntityExtractor, LLMRelationExtractor, CombinedExtractor
from app.modules.graph.builder import KnowledgeGraphBuilder, GraphBuilderFactory
from app.modules.graph.storage import JSONFileGraphStorage, InMemoryGraphStorage, GraphStorageManager


class TestLLMEntityExtractor(unittest.TestCase):
    """测试 LLMEntityExtractor 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.mock_llm_client = Mock()
        self.mock_llm_client.chat = Mock(return_value='{"entities": [{"name": "测试实体", "type": "人物", "description": "测试描述"}]}')
    
    def test_init_with_llm_client(self):
        """测试初始化"""
        extractor = LLMEntityExtractor(self.mock_llm_client)
        self.assertIsNotNone(extractor)
        self.assertEqual(extractor.llm_client, self.mock_llm_client)
    
    def test_extract_empty_text(self):
        """测试空文本提取"""
        extractor = LLMEntityExtractor(self.mock_llm_client)
        result = extractor.extract("")
        self.assertEqual(result, [])
    
    def test_extract_whitespace_text(self):
        """测试空白文本提取"""
        extractor = LLMEntityExtractor(self.mock_llm_client)
        result = extractor.extract("   ")
        self.assertEqual(result, [])
    
    def test_extract_with_entities(self):
        """测试正常提取"""
        extractor = LLMEntityExtractor(self.mock_llm_client)
        result = extractor.extract("测试文本")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "测试实体")
        self.assertEqual(result[0]["type"], "人物")
    
    def test_extract_with_invalid_json(self):
        """测试无效 JSON 响应"""
        self.mock_llm_client.chat = Mock(return_value="无效的 JSON")
        extractor = LLMEntityExtractor(self.mock_llm_client)
        
        result = extractor.extract("测试文本")
        self.assertEqual(result, [])
    
    def test_extract_with_empty_entities(self):
        """测试空实体列表响应"""
        self.mock_llm_client.chat = Mock(return_value='{"entities": []}')
        extractor = LLMEntityExtractor(self.mock_llm_client)
        
        result = extractor.extract("测试文本")
        self.assertEqual(result, [])
    
    def test_extract_with_entity_types_filter(self):
        """测试实体类型过滤"""
        extractor = LLMEntityExtractor(self.mock_llm_client)
        result = extractor.extract("测试文本", entity_types=["人物", "组织"])
        
        self.mock_llm_client.chat.assert_called_once()
        call_args = self.mock_llm_client.chat.call_args
        self.assertIn("只提取以下类型的实体", call_args[1]["message"])
    
    def test_default_system_prompt(self):
        """测试默认系统提示词"""
        extractor = LLMEntityExtractor(self.mock_llm_client)
        self.assertIn("实体提取助手", extractor.system_prompt)
    
    def test_extract_with_attributes(self):
        """测试带属性的实体提取"""
        self.mock_llm_client.chat = Mock(return_value='{"entities": [{"name": "公司A", "type": "组织", "description": "科技公司", "attributes": {"成立时间": "2020年"}}]}')
        extractor = LLMEntityExtractor(self.mock_llm_client)
        
        result = extractor.extract_with_attributes("测试文本", ["成立时间"])
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["attributes"]["成立时间"], "2020年")


class TestLLMRelationExtractor(unittest.TestCase):
    """测试 LLMRelationExtractor 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.mock_llm_client = Mock()
        self.mock_llm_client.chat = Mock(return_value='{"relations": [{"source": "实体A", "target": "实体B", "type": "合作关系", "description": "测试关系"}]}')
    
    def test_init_with_llm_client(self):
        """测试初始化"""
        extractor = LLMRelationExtractor(self.mock_llm_client)
        self.assertIsNotNone(extractor)
        self.assertEqual(extractor.llm_client, self.mock_llm_client)
    
    def test_extract_empty_entities(self):
        """测试空实体列表"""
        extractor = LLMRelationExtractor(self.mock_llm_client)
        result = extractor.extract([], "测试文本")
        self.assertEqual(result, [])
    
    def test_extract_empty_text(self):
        """测试空文本"""
        extractor = LLMRelationExtractor(self.mock_llm_client)
        entities = [{"name": "实体A", "type": "人物"}]
        result = extractor.extract(entities, "")
        self.assertEqual(result, [])
    
    def test_extract_with_relations(self):
        """测试正常提取"""
        entities = [{"name": "实体A", "type": "人物", "description": "描述"}]
        extractor = LLMRelationExtractor(self.mock_llm_client)
        result = extractor.extract(entities, "测试文本")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "实体A")
        self.assertEqual(result[0]["target"], "实体B")
        self.assertEqual(result[0]["type"], "合作关系")
    
    def test_extract_with_invalid_json(self):
        """测试无效 JSON 响应"""
        self.mock_llm_client.chat = Mock(return_value="无效的 JSON")
        extractor = LLMRelationExtractor(self.mock_llm_client)
        
        entities = [{"name": "实体A", "type": "人物"}]
        result = extractor.extract(entities, "测试文本")
        self.assertEqual(result, [])
    
    def test_extract_with_relation_types_filter(self):
        """测试关系类型过滤"""
        entities = [{"name": "实体A", "type": "人物"}]
        extractor = LLMRelationExtractor(self.mock_llm_client)
        result = extractor.extract(entities, "测试文本", relation_types=["合作关系"])
        
        call_args = self.mock_llm_client.chat.call_args
        self.assertIn("只提取以下类型的关系", call_args[1]["message"])


class TestCombinedExtractor(unittest.TestCase):
    """测试 CombinedExtractor 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.mock_llm_client = Mock()
        self.mock_llm_client.chat = Mock(return_value='{"entities": [{"name": "实体A", "type": "人物"}], "relations": []}')
    
    def test_extract_all_empty_text(self):
        """测试空文本"""
        extractor = CombinedExtractor(self.mock_llm_client)
        result = extractor.extract_all("")
        self.assertEqual(result, {"entities": [], "relations": []})
    
    def test_extract_all_no_entities(self):
        """测试无实体"""
        self.mock_llm_client.chat = Mock(return_value='{"entities": []}')
        extractor = CombinedExtractor(self.mock_llm_client)
        result = extractor.extract_all("测试文本")
        self.assertEqual(result, {"entities": [], "relations": []})


class TestKnowledgeGraphBuilder(unittest.TestCase):
    """测试 KnowledgeGraphBuilder 类"""
    
    def test_init_with_custom_id(self):
        """测试带自定义 ID 初始化"""
        builder = KnowledgeGraphBuilder("test-graph-123")
        self.assertEqual(builder.graph_id, "test-graph-123")
    
    def test_init_without_id(self):
        """测试自动生成 ID"""
        builder = KnowledgeGraphBuilder()
        self.assertIsNotNone(builder.graph_id)
        self.assertTrue(len(builder.graph_id) > 0)
    
    def test_build_with_entities_and_relations(self):
        """测试构建图谱"""
        builder = KnowledgeGraphBuilder()
        entities = [
            {"name": "张三", "type": "人物", "description": "CEO"},
            {"name": "公司A", "type": "组织", "description": "科技公司"}
        ]
        relations = [
            {"source": "张三", "target": "公司A", "type": "创立", "description": "创立了公司"}
        ]
        
        graph = builder.build(entities, relations)
        
        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(len(graph["edges"]), 1)
        self.assertEqual(graph["nodes"][0]["id"], "张三")
        self.assertEqual(graph["edges"][0]["type"], "创立")
    
    def test_build_with_source_text(self):
        """测试带源文本构建"""
        builder = KnowledgeGraphBuilder()
        entities = [{"name": "实体", "type": "人物"}]
        
        graph = builder.build(entities, [], source_text="这是源文本", description="测试描述")
        
        self.assertEqual(graph["metadata"]["source_text"], "这是源文本")
        self.assertEqual(graph["metadata"]["description"], "测试描述")
    
    def test_add_node(self):
        """测试添加节点"""
        builder = KnowledgeGraphBuilder()
        result = builder.add_node({"id": "test-node", "type": "测试", "description": "测试节点"})
        
        self.assertTrue(result)
        self.assertEqual(len(builder.graph["nodes"]), 1)
        self.assertEqual(builder.graph["nodes"][0]["id"], "test-node")
    
    def test_add_node_duplicate(self):
        """测试添加重复节点"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "test-node", "type": "测试"})
        result = builder.add_node({"id": "test-node", "type": "测试"})
        
        self.assertFalse(result)
        self.assertEqual(len(builder.graph["nodes"]), 1)
    
    def test_add_node_without_id(self):
        """测试添加无 ID 节点"""
        builder = KnowledgeGraphBuilder()
        result = builder.add_node({"type": "测试"})
        
        self.assertFalse(result)
        self.assertEqual(len(builder.graph["nodes"]), 0)
    
    def test_add_edge(self):
        """测试添加边"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1", "type": "人物"})
        builder.add_node({"id": "node2", "type": "组织"})
        
        result = builder.add_edge("node1", "node2", "合作关系", "测试描述")
        
        self.assertTrue(result)
        self.assertEqual(len(builder.graph["edges"]), 1)
        self.assertEqual(builder.graph["edges"][0]["type"], "合作关系")
    
    def test_add_edge_missing_nodes(self):
        """测试添加不存在的节点的边"""
        builder = KnowledgeGraphBuilder()
        result = builder.add_edge("nonexistent", "node2", "合作关系")
        
        self.assertFalse(result)
    
    def test_add_edge_duplicate(self):
        """测试添加重复边"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1", "type": "人物"})
        builder.add_node({"id": "node2", "type": "组织"})
        
        builder.add_edge("node1", "node2", "合作关系")
        result = builder.add_edge("node1", "node2", "合作关系")
        
        self.assertFalse(result)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1", "type": "人物"})
        builder.add_node({"id": "node2", "type": "人物"})
        builder.add_node({"id": "node3", "type": "组织"})
        builder.add_edge("node1", "node2", "朋友")
        
        stats = builder.get_statistics()
        
        self.assertEqual(stats["total_nodes"], 3)
        self.assertEqual(stats["total_edges"], 1)
        self.assertIn("人物", stats["node_types"])
        self.assertEqual(stats["node_types"]["人物"], 2)
        self.assertEqual(stats["avg_degree"], 2 / 3)
    
    def test_get_node(self):
        """测试获取节点"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "test-node", "type": "测试", "description": "测试描述"})
        
        node = builder.get_node("test-node")
        
        self.assertIsNotNone(node)
        self.assertEqual(node["id"], "test-node")
        self.assertEqual(node["description"], "测试描述")
    
    def test_get_node_not_found(self):
        """测试获取不存在的节点"""
        builder = KnowledgeGraphBuilder()
        node = builder.get_node("nonexistent")
        
        self.assertIsNone(node)
    
    def test_get_neighbors(self):
        """测试获取邻居节点"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1", "type": "人物"})
        builder.add_node({"id": "node2", "type": "人物"})
        builder.add_edge("node1", "node2", "朋友")
        
        neighbors = builder.get_neighbors("node1")
        
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]["node"]["id"], "node2")
        self.assertEqual(neighbors[0]["relation"], "朋友")
    
    def test_search_nodes(self):
        """测试搜索节点"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "张三", "type": "人物", "description": "CEO"})
        builder.add_node({"id": "李四", "type": "人物", "description": "CTO"})
        builder.add_node({"id": "王五", "type": "组织", "description": "技术团队"})
        
        results = builder.search_nodes("张")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "张三")
    
    def test_to_cytoscape_format(self):
        """测试转换为 Cytoscape 格式"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1", "type": "人物"})
        builder.add_node({"id": "node2", "type": "组织"})
        builder.add_edge("node1", "node2", "创立")
        
        cytoscape = builder.to_cytoscape_format()
        
        self.assertIn("elements", cytoscape)
        self.assertIn("style", cytoscape)
        self.assertEqual(len(cytoscape["elements"]), 3)
    
    def test_to_networkx_format(self):
        """测试转换为 NetworkX 格式"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1", "type": "人物"})
        builder.add_node({"id": "node2", "type": "组织"})
        builder.add_edge("node1", "node2", "创立")
        
        networkx = builder.to_networkx_format()
        
        self.assertIn("nodes", networkx)
        self.assertIn("edges", networkx)
        self.assertEqual(len(networkx["nodes"]), 2)
        self.assertEqual(len(networkx["edges"]), 1)
        self.assertTrue(networkx["directed"])
    
    def test_merge_graph(self):
        """测试合并图谱"""
        builder1 = KnowledgeGraphBuilder()
        builder1.add_node({"id": "node1", "type": "人物"})
        builder1.add_node({"id": "node2", "type": "组织"})
        
        builder2 = KnowledgeGraphBuilder()
        builder2.add_node({"id": "node3", "type": "人物"})
        builder2.add_node({"id": "node4", "type": "组织"})
        
        result = builder1.merge_graph(builder2.graph)
        
        self.assertTrue(result)
        self.assertEqual(len(builder1.graph["nodes"]), 4)
    
    def test_clear(self):
        """测试清空图谱"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1", "type": "人物"})
        builder.add_edge("node1", "node2", "关系")
        
        builder.clear()
        
        self.assertEqual(len(builder.graph["nodes"]), 0)
        self.assertEqual(len(builder.graph["edges"]), 0)
    
    def test_get_edges_by_type(self):
        """测试按类型获取边"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1"})
        builder.add_node({"id": "node2"})
        builder.add_node({"id": "node3"})
        builder.add_edge("node1", "node2", "朋友")
        builder.add_edge("node2", "node3", "朋友")
        builder.add_edge("node1", "node3", "同事")
        
        friend_edges = builder.get_edges_by_type("朋友")
        
        self.assertEqual(len(friend_edges), 2)
    
    def test_get_nodes_by_type(self):
        """测试按类型获取节点"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1", "type": "人物"})
        builder.add_node({"id": "node2", "type": "人物"})
        builder.add_node({"id": "node3", "type": "组织"})
        
        person_nodes = builder.get_nodes_by_type("人物")
        
        self.assertEqual(len(person_nodes), 2)
    
    def test_update_metadata(self):
        """测试更新元数据"""
        builder = KnowledgeGraphBuilder()
        builder.update_metadata("author", "测试作者")
        
        self.assertEqual(builder.graph["metadata"]["author"], "测试作者")
    
    def test_get_graph(self):
        """测试获取图谱"""
        builder = KnowledgeGraphBuilder()
        builder.add_node({"id": "node1"})
        
        graph = builder.get_graph()
        
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)


class TestGraphBuilderFactory(unittest.TestCase):
    """测试 GraphBuilderFactory 类"""
    
    def test_create_builder(self):
        """测试创建标准构建器"""
        builder = GraphBuilderFactory.create_builder("test-id")
        
        self.assertIsInstance(builder, KnowledgeGraphBuilder)
        self.assertEqual(builder.graph_id, "test-id")
    
    def test_create_social_graph_builder(self):
        """测试创建社交图谱构建器"""
        builder = GraphBuilderFactory.create_social_graph_builder()
        
        self.assertEqual(builder.graph["metadata"]["graph_type"], "social_network")
    
    def test_create_knowledge_graph_builder(self):
        """测试创建知识图谱构建器"""
        builder = GraphBuilderFactory.create_knowledge_graph_builder()
        
        self.assertEqual(builder.graph["metadata"]["graph_type"], "knowledge_graph")


class TestJSONFileGraphStorage(unittest.TestCase):
    """测试 JSONFileGraphStorage 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_init_creates_directory(self):
        """测试初始化创建目录"""
        new_dir = os.path.join(self.test_dir, "new_subdir")
        storage = JSONFileGraphStorage(new_dir)
        
        self.assertTrue(os.path.exists(new_dir))
    
    def test_save_and_load(self):
        """测试保存和加载"""
        storage = JSONFileGraphStorage(self.test_dir)
        graph_data = {"id": "test-graph", "nodes": [{"id": "node1"}], "edges": []}
        
        result = storage.save("test-graph", graph_data)
        self.assertTrue(result)
        
        loaded = storage.load("test-graph")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["id"], "test-graph")
        self.assertEqual(len(loaded["nodes"]), 1)
    
    def test_load_nonexistent(self):
        """测试加载不存在的图谱"""
        storage = JSONFileGraphStorage(self.test_dir)
        result = storage.load("nonexistent")
        
        self.assertIsNone(result)
    
    def test_exists(self):
        """测试存在性检查"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("existing-graph", {"nodes": []})
        
        self.assertTrue(storage.exists("existing-graph"))
        self.assertFalse(storage.exists("nonexistent"))
    
    def test_delete(self):
        """测试删除"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("to-delete", {"nodes": []})
        
        result = storage.delete("to-delete")
        self.assertTrue(result)
        self.assertFalse(storage.exists("to-delete"))
    
    def test_delete_nonexistent(self):
        """测试删除不存在的图谱"""
        storage = JSONFileGraphStorage(self.test_dir)
        result = storage.delete("nonexistent")
        
        self.assertFalse(result)
    
    def test_list_graphs(self):
        """测试列出图谱"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("graph1", {"nodes": [{"id": "n1"}], "edges": []})
        storage.save("graph2", {"nodes": [{"id": "n2"}, {"id": "n3"}], "edges": []})
        
        graphs = storage.list_graphs()
        
        self.assertEqual(len(graphs), 2)
    
    def test_list_graphs_with_metadata(self):
        """测试带元数据列出图谱"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("graph1", {"nodes": [{"id": "n1"}], "edges": []})
        
        graphs = storage.list_graphs(include_metadata=True)
        
        self.assertEqual(len(graphs), 1)
        self.assertIn("node_count", graphs[0])
        self.assertEqual(graphs[0]["node_count"], 1)
    
    def test_update(self):
        """测试更新"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("test-graph", {"nodes": [], "edges": []})
        
        result = storage.update("test-graph", {"nodes": [{"id": "new-node"}]})
        self.assertTrue(result)
        
        loaded = storage.load("test-graph")
        self.assertEqual(len(loaded["nodes"]), 1)
    
    def test_get_storage_stats(self):
        """测试存储统计"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("graph1", {"nodes": [{"id": "n1"}], "edges": []})
        storage.save("graph2", {"nodes": [{"id": "n2"}], "edges": []})
        
        stats = storage.get_storage_stats()
        
        self.assertEqual(stats["total_graphs"], 2)
        self.assertEqual(stats["total_nodes"], 2)
    
    def test_load_with_metadata(self):
        """测试加载带元数据"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("test-graph", {"id": "test", "nodes": [], "edges": []})
        
        result = storage.load_with_metadata("test-graph")
        
        self.assertIn("graph", result)
        self.assertIn("file_info", result)
    
    def test_backup_and_restore(self):
        """测试备份和恢复"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("test-graph", {"id": "test-graph", "nodes": [], "edges": []})
        
        backup_path = storage.backup("test-graph")
        self.assertIsNotNone(backup_path)
        
        storage.delete("test-graph")
        self.assertFalse(storage.exists("test-graph"))
        
        result = storage.restore(backup_path)
        self.assertTrue(result)
        self.assertTrue(storage.exists("test-graph"))
    
    def test_export_to_json(self):
        """测试导出到 JSON"""
        storage = JSONFileGraphStorage(self.test_dir)
        storage.save("test-graph", {"nodes": [], "edges": []})
        
        export_path = storage.export_to_json("test-graph")
        self.assertIsNotNone(export_path)
        
        self.assertTrue(os.path.exists(export_path))


class TestInMemoryGraphStorage(unittest.TestCase):
    """测试 InMemoryGraphStorage 类"""
    
    def test_save_and_load(self):
        """测试保存和加载"""
        storage = InMemoryGraphStorage()
        graph_data = {"id": "test-graph", "nodes": [], "edges": []}
        
        result = storage.save("test-graph", graph_data)
        self.assertTrue(result)
        
        loaded = storage.load("test-graph")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["id"], "test-graph")
    
    def test_exists(self):
        """测试存在性检查"""
        storage = InMemoryGraphStorage()
        storage.save("existing", {"nodes": []})
        
        self.assertTrue(storage.exists("existing"))
        self.assertFalse(storage.exists("nonexistent"))
    
    def test_delete(self):
        """测试删除"""
        storage = InMemoryGraphStorage()
        storage.save("to-delete", {"nodes": []})
        
        result = storage.delete("to-delete")
        self.assertTrue(result)
        self.assertFalse(storage.exists("to-delete"))
    
    def test_clear(self):
        """测试清空"""
        storage = InMemoryGraphStorage()
        storage.save("graph1", {"nodes": []})
        storage.save("graph2", {"nodes": []})
        
        storage.clear()
        
        self.assertEqual(len(storage.list_graphs()), 0)
    
    def test_get_all(self):
        """测试获取所有"""
        storage = InMemoryGraphStorage()
        storage.save("graph1", {"id": "g1", "nodes": []})
        storage.save("graph2", {"id": "g2", "nodes": []})
        
        all_graphs = storage.get_all()
        
        self.assertEqual(len(all_graphs), 2)
        self.assertIn("graph1", all_graphs)
        self.assertIn("graph2", all_graphs)
    
    def test_list_graphs(self):
        """测试列出图谱"""
        storage = InMemoryGraphStorage()
        storage.save("g1", {"nodes": []})
        storage.save("g2", {"nodes": []})
        
        graphs = storage.list_graphs()
        
        self.assertEqual(len(graphs), 2)


class TestGraphStorageManager(unittest.TestCase):
    """测试 GraphStorageManager 类"""
    
    def test_init_with_file_storage(self):
        """测试文件存储初始化"""
        test_dir = tempfile.mkdtemp()
        manager = GraphStorageManager(storage_type="file", storage_dir=test_dir)
        
        self.assertIsInstance(manager.storage, JSONFileGraphStorage)
        
        import shutil
        shutil.rmtree(test_dir)
    
    def test_init_with_memory_storage(self):
        """测试内存存储初始化"""
        manager = GraphStorageManager(storage_type="memory")
        
        self.assertIsInstance(manager.storage, InMemoryGraphStorage)
    
    def test_save_and_load(self):
        """测试保存和加载"""
        manager = GraphStorageManager(storage_type="memory")
        graph_data = {"id": "test", "nodes": [], "edges": []}
        
        manager.save_graph("test", graph_data)
        loaded = manager.load_graph("test")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["id"], "test")
    
    def test_list_graphs(self):
        """测试列出图谱"""
        manager = GraphStorageManager(storage_type="memory")
        manager.save_graph("g1", {"nodes": []})
        manager.save_graph("g2", {"nodes": []})
        
        graphs = manager.list_graphs()
        
        self.assertEqual(len(graphs), 2)
    
    def test_delete_graph(self):
        """测试删除图谱"""
        manager = GraphStorageManager(storage_type="memory")
        manager.save_graph("to-delete", {"nodes": []})
        
        result = manager.delete_graph("to-delete")
        self.assertTrue(result)
        self.assertIsNone(manager.load_graph("to-delete"))
    
    def test_graph_exists(self):
        """测试图谱存在性"""
        manager = GraphStorageManager(storage_type="memory")
        manager.save_graph("existing", {"nodes": []})
        
        self.assertTrue(manager.graph_exists("existing"))
        self.assertFalse(manager.graph_exists("nonexistent"))
    
    def test_get_statistics(self):
        """测试获取统计"""
        manager = GraphStorageManager(storage_type="memory")
        manager.save_graph("g1", {"nodes": [{"id": "n1"}], "edges": []})
        manager.save_graph("g2", {"nodes": [{"id": "n2"}], "edges": []})
        
        stats = manager.get_statistics()
        
        self.assertEqual(stats["total_graphs"], 2)
        self.assertEqual(stats["total_nodes"], 2)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_pipeline(self):
        """测试完整流程"""
        builder = KnowledgeGraphBuilder("pipeline-test")
        
        entities = [
            {"name": "张三", "type": "人物", "description": "CEO"},
            {"name": "公司A", "type": "组织", "description": "科技公司"},
            {"name": "李四", "type": "人物", "description": "CTO"}
        ]
        relations = [
            {"source": "张三", "target": "公司A", "type": "创立", "description": "创立公司"},
            {"source": "李四", "target": "公司A", "type": "任职", "description": "担任CTO"},
            {"source": "张三", "target": "李四", "type": "同事", "description": "同事关系"}
        ]
        
        graph = builder.build(entities, relations, source_text="测试文本")
        
        storage = InMemoryGraphStorage()
        storage.save("pipeline-test", graph)
        
        loaded = storage.load("pipeline-test")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded["nodes"]), 3)
        self.assertEqual(len(loaded["edges"]), 3)
        
        stats = builder.get_statistics()
        self.assertEqual(stats["total_nodes"], 3)
        self.assertEqual(stats["total_edges"], 3)
    
    def test_storage_manager_workflow(self):
        """测试存储管理器工作流程"""
        test_dir = tempfile.mkdtemp()
        try:
            manager = GraphStorageManager(storage_type="file", storage_dir=test_dir)
            
            graph_data = {
                "id": "workflow-test",
                "nodes": [{"id": "node1", "type": "人物"}],
                "edges": []
            }
            
            manager.save_graph("workflow-test", graph_data)
            
            self.assertTrue(manager.graph_exists("workflow-test"))
            
            graphs = manager.list_graphs(include_metadata=True)
            self.assertEqual(len(graphs), 1)
            
            stats = manager.get_statistics()
            self.assertEqual(stats["total_graphs"], 1)
            
            loaded = manager.load_graph("workflow-test")
            self.assertIsNotNone(loaded)
            
            result = manager.delete_graph("workflow-test")
            self.assertTrue(result)
            self.assertFalse(manager.graph_exists("workflow-test"))
        finally:
            import shutil
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
