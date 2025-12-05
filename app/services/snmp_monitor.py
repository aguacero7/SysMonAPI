import asyncio
import time
from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from easysnmp import Session as SNMPSession, EasySNMPTimeoutError, EasySNMPError
from app.models import Router, SNMPMetric
from app.config.database import engine
import logging

logger = logging.getLogger(__name__)

class SNMPMonitor:
    """service de monitoring snmp qui tourne en arriere-plan"""

    def __init__(self, poll_interval: int = 60, community: str = "public"):
        self.poll_interval = poll_interval  # intervalle en secondes entre les polls
        self.community = community  # communaute snmp
        self.is_running = False
        self.task: Optional[asyncio.Task] = None

        # oids snmp standards
        self.oids = {
            'system_uptime': '1.3.6.1.2.1.1.3.0',
            'if_in_octets': '1.3.6.1.2.1.2.2.1.10',  # pour interface 1
            'if_out_octets': '1.3.6.1.2.1.2.2.1.16',
            'if_in_errors': '1.3.6.1.2.1.2.2.1.14',
            'if_out_errors': '1.3.6.1.2.1.2.2.1.20',
            'if_oper_status': '1.3.6.1.2.1.2.2.1.8',
        }

    def get_snmp_value(self, host: str, oid: str) -> tuple[bool, Optional[str], Optional[float]]:
        start_time = time.time()

        try:
            session = SNMPSession(
                hostname=host,
                community=self.community,
                version=2,
                timeout=5,
                retries=1
            )

            result = session.get(oid)
            response_time = (time.time() - start_time) * 1000  # en ms

            if result and result.value:
                return True, result.value, response_time
            else:
                logger.error(f"snmp error for {host}: no value returned")
                return False, None, response_time

        except EasySNMPTimeoutError as e:
            logger.error(f"snmp timeout for {host}: {e}")
            response_time = (time.time() - start_time) * 1000
            return False, None, response_time
        except EasySNMPError as e:
            logger.error(f"snmp error for {host}: {e}")
            response_time = (time.time() - start_time) * 1000
            return False, None, response_time
        except Exception as e:
            logger.error(f"exception during snmp poll for {host}: {e}")
            response_time = (time.time() - start_time) * 1000
            return False, None, response_time

    def collect_router_metrics(self, router: Router) -> Optional[SNMPMetric]:
        host = router.ip
        logger.info(f"collecting snmp metrics from {host}")

        success, uptime, response_time = self.get_snmp_value(host, self.oids['system_uptime'])

        if not success:
            metric = SNMPMetric(
                router_id=router.id,
                is_reachable=False,
                response_time=response_time,
                timestamp=datetime.utcnow()
            )
            return metric

        metric = SNMPMetric(
            router_id=router.id,
            is_reachable=True,
            response_time=response_time,
            timestamp=datetime.utcnow()
        )

    
        if uptime:
            try:
                metric.system_uptime = int(uptime)
            except ValueError:
                pass

        success, value, _ = self.get_snmp_value(host, f"{self.oids['if_in_octets']}.1")
        if success and value:
            try:
                metric.if_in_octets = int(value)
            except ValueError:
                pass

        success, value, _ = self.get_snmp_value(host, f"{self.oids['if_out_octets']}.1")
        if success and value:
            try:
                metric.if_out_octets = int(value)
            except ValueError:
                pass

        success, value, _ = self.get_snmp_value(host, f"{self.oids['if_in_errors']}.1")
        if success and value:
            try:
                metric.if_in_errors = int(value)
            except ValueError:
                pass

        success, value, _ = self.get_snmp_value(host, f"{self.oids['if_out_errors']}.1")
        if success and value:
            try:
                metric.if_out_errors = int(value)
            except ValueError:
                pass

        success, value, _ = self.get_snmp_value(host, f"{self.oids['if_oper_status']}.1")
        if success and value:
            try:
                metric.if_oper_status = int(value)
            except ValueError:
                pass

        return metric

    def poll_all_routers(self):

        with Session(engine) as session:
            # recupere tous les routeurs
            statement = select(Router)
            routers = session.exec(statement).all()

            logger.info(f"polling {len(routers)} routers")

            for router in routers:
                try:
                    metric = self.collect_router_metrics(router)
                    if metric:
                        session.add(metric)
                        session.commit()
                        logger.info(f"saved metrics for router {router.id} ({router.ip})")
                except Exception as e:
                    logger.error(f"error collecting metrics for router {router.id}: {e}")
                    session.rollback()

    async def monitor_loop(self):
        """boucle principale de monitoring"""
        logger.info(f"snmp monitor started with {self.poll_interval}s interval")

        while self.is_running:
            try:
                await asyncio.get_event_loop().run_in_executor(None, self.poll_all_routers)
            except Exception as e:
                logger.error(f"error in monitor loop: {e}")

            await asyncio.sleep(self.poll_interval)

        logger.info("snmp monitor stopped")

    async def start(self):
        if self.is_running:
            logger.warning("snmp monitor already running")
            return

        self.is_running = True
        self.task = asyncio.create_task(self.monitor_loop())
        logger.info("snmp monitor task created")

    async def stop(self):
        if not self.is_running:
            return

        self.is_running = False
        if self.task:
            await self.task
        logger.info("snmp monitor stopped")

snmp_monitor = SNMPMonitor(poll_interval=60, community="public")
