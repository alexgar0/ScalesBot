from tools._internal.registry import DependencyRegistry
from tools.skills.deps import SkillDeps
from tools.requests.deps import RequestsDeps


AgentDependencies = DependencyRegistry.get_combined_deps_type()
