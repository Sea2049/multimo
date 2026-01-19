# 重试机制模块

import time
import functools
from typing import Callable, Type, Tuple, Any, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


def retry_with_backoff(max_retries: int = 3, 
                      backoff_factor: float = 2.0,
                      max_wait: float = 60.0,
                      exceptions: Tuple[Type[Exception], ...] = Exception,
                      on_retry: Optional[Callable[[Exception, int], None]] = None):
    """带指数退避的重试装饰器
    
    Args:
        max_retries: 最大重试次数
        backoff_factor: 退避因子（每次重试的等待时间乘以该因子）
        max_wait: 最大等待时间（秒）
        exceptions: 需要重试的异常类型元组
        on_retry: 重试时的回调函数，接收（异常，重试次数）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            wait_time = 1.0  # 初始等待时间
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    
                    if retries > max_retries:
                        logger.error(f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败")
                        raise
                    
                    # 计算等待时间（带上限）
                    wait_time = min(wait_time * backoff_factor, max_wait)
                    
                    logger.warning(
                        f"函数 {func.__name__} 执行失败（第 {retries} 次重试），"
                        f"{wait_time:.2f}秒后重试。错误: {e}"
                    )
                    
                    # 调用回调函数
                    if on_retry:
                        on_retry(e, retries)
                    
                    # 等待
                    time.sleep(wait_time)
            
            # 理论上不会执行到这里
            raise RuntimeError("重试逻辑错误")
        
        return wrapper
    return decorator


def retry_on_condition(max_retries: int = 3,
                      check_condition: Callable[[Any], bool] = lambda x: x is None,
                      exceptions: Tuple[Type[Exception], ...] = Exception,
                      on_retry: Optional[Callable[[Any, int], None]] = None):
    """基于返回条件的重试装饰器
    
    Args:
        max_retries: 最大重试次数
        check_condition: 检查返回值的条件函数，返回 True 则重试
        exceptions: 需要捕获的异常类型
        on_retry: 重试时的回调函数，接收（返回值，重试次数）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # 检查条件
                    if check_condition(result):
                        if attempt < max_retries:
                            logger.warning(
                                f"函数 {func.__name__} 返回值不符合条件（第 {attempt + 1} 次尝试），"
                                f"将进行第 {attempt + 2} 次重试"
                            )
                            
                            if on_retry:
                                on_retry(result, attempt + 1)
                            
                            time.sleep(1.0)
                            continue
                        else:
                            logger.error(f"函数 {func.__name__} 重试 {max_retries} 次后仍不符合条件")
                    
                    return result
                    
                except exceptions as e:
                    if attempt < max_retries:
                        logger.warning(
                            f"函数 {func.__name__} 执行失败（第 {attempt + 1} 次尝试），"
                            f"将进行第 {attempt + 2} 次重试。错误: {e}"
                        )
                        
                        if on_retry:
                            on_retry(e, attempt + 1)
                        
                        time.sleep(1.0)
                        continue
                    else:
                        logger.error(f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败")
                        raise
            
            # 理论上不会执行到这里
            raise RuntimeError("重试逻辑错误")
        
        return wrapper
    return decorator


class RetryPolicy:
    """重试策略类"""
    
    def __init__(self, max_retries: int = 3,
                 backoff_factor: float = 2.0,
                 max_wait: float = 60.0,
                 initial_wait: float = 1.0):
        """初始化重试策略
        
        Args:
            max_retries: 最大重试次数
            backoff_factor: 退避因子
            max_wait: 最大等待时间
            initial_wait: 初始等待时间
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_wait = max_wait
        self.initial_wait = initial_wait
        self.retry_count = 0
    
    def get_wait_time(self) -> float:
        """获取当前等待时间"""
        wait_time = self.initial_wait * (self.backoff_factor ** self.retry_count)
        return min(wait_time, self.max_wait)
    
    def should_retry(self) -> bool:
        """检查是否应该重试"""
        return self.retry_count < self.max_retries
    
    def increment(self):
        """增加重试计数"""
        self.retry_count += 1
    
    def reset(self):
        """重置重试计数"""
        self.retry_count = 0


def retry_with_policy(policy: RetryPolicy,
                    exceptions: Tuple[Type[Exception], ...] = Exception):
    """使用自定义重试策略的装饰器
    
    Args:
        policy: 重试策略对象
        exceptions: 需要重试的异常类型
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            policy.reset()
            
            while policy.should_retry():
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if not policy.should_retry():
                        logger.error(
                            f"函数 {func.__name__} 重试 {policy.retry_count} 次后仍然失败"
                        )
                        raise
                    
                    wait_time = policy.get_wait_time()
                    policy.increment()
                    
                    logger.warning(
                        f"函数 {func.__name__} 执行失败（第 {policy.retry_count} 次重试），"
                        f"{wait_time:.2f}秒后重试。错误: {e}"
                    )
                    
                    time.sleep(wait_time)
            
            # 理论上不会执行到这里
            raise RuntimeError("重试逻辑错误")
        
        return wrapper
    return decorator


def retry_circuit_breaker(max_failures: int = 5,
                         recovery_timeout: float = 60.0):
    """断路器模式的重试装饰器
    
    当连续失败次数达到阈值时，暂时停止重试
    
    Args:
        max_failures: 最大失败次数（触发断路器）
        recovery_timeout: 恢复超时时间（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        # 断路器状态
        failure_count = 0
        last_failure_time = None
        circuit_open = False
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            nonlocal failure_count, last_failure_time, circuit_open
            
            # 检查断路器是否开启
            if circuit_open:
                # 检查是否可以尝试恢复
                if last_failure_time and time.time() - last_failure_time > recovery_timeout:
                    logger.info(f"断路器尝试恢复: {func.__name__}")
                    circuit_open = False
                    failure_count = 0
                else:
                    raise RuntimeError(
                        f"断路器已开启，{func.__name__} 暂时不可用。"
                        f"预计 {recovery_timeout:.0f} 秒后恢复"
                    )
            
            try:
                result = func(*args, **kwargs)
                
                # 成功，重置断路器
                if circuit_open or failure_count > 0:
                    logger.info(f"函数 {func.__name__} 执行成功，重置断路器")
                circuit_open = False
                failure_count = 0
                
                return result
                
            except Exception as e:
                failure_count += 1
                last_failure_time = time.time()
                
                logger.error(
                    f"函数 {func.__name__} 执行失败（第 {failure_count} 次连续失败）。错误: {e}"
                )
                
                # 检查是否需要开启断路器
                if failure_count >= max_failures:
                    circuit_open = True
                    logger.warning(
                        f"断路器已开启：{func.__name__}，连续失败 {failure_count} 次"
                    )
                
                raise
        
        return wrapper
    return decorator


class RetryExecutor:
    """重试执行器，支持复杂重试逻辑"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        """初始化重试执行器
        
        Args:
            max_retries: 最大重试次数
            backoff_factor: 退避因子
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = get_logger(__name__)
    
    def execute(self, func: Callable, *args, 
                exceptions: Tuple[Type[Exception], ...] = Exception,
                on_retry: Optional[Callable] = None, **kwargs) -> Any:
        """执行函数并重试
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            exceptions: 需要捕获的异常类型
            on_retry: 重试时的回调函数
            **kwargs: 关键字参数
            
        Returns:
            函数执行结果
        """
        retries = 0
        wait_time = 1.0
        
        while retries <= self.max_retries:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                retries += 1
                
                if retries > self.max_retries:
                    self.logger.error(
                        f"函数 {func.__name__} 重试 {self.max_retries} 次后仍然失败"
                    )
                    raise
                
                wait_time = min(wait_time * self.backoff_factor, 60.0)
                
                self.logger.warning(
                    f"函数 {func.__name__} 执行失败（第 {retries} 次重试），"
                    f"{wait_time:.2f}秒后重试。错误: {e}"
                )
                
                if on_retry:
                    on_retry(e, retries)
                
                time.sleep(wait_time)
        
        raise RuntimeError("重试逻辑错误")
