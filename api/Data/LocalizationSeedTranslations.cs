using System.Collections.Generic;

namespace StudyTracker.Api.Data;

/// <summary>
/// Vendor-delivered translations for the two seeded locales whose marketplace jobs are past the
/// "vendor is still working" point: fr-FR (Submitted for Review) and es-ES (Approved). A job can
/// only reach those states once every string has target text, so the seed has to supply it.
/// Keyed by LocalizationString.Key.
/// </summary>
public static class LocalizationSeedTranslations
{
    public static readonly IReadOnlyDictionary<string, (string French, string Spanish)> ByKey =
        new Dictionary<string, (string French, string Spanish)>
        {
            ["hud.speed.label"] = ("Vitesse actuelle", "Velocidad actual"),
            ["hud.warning.lowfuel"] = ("Alerte niveau de carburant bas", "Aviso de nivel de combustible bajo"),
            ["hud.nav.turnleft"] = ("Tournez à gauche plus loin", "Gire a la izquierda más adelante"),
            ["hud.climate.temp"] = ("Température de l'habitacle", "Temperatura del habitáculo"),
            ["hud.alert.doorajar"] = ("Porte mal fermée", "Puerta mal cerrada"),
            ["hud.gear.reverse"] = ("Marche arrière engagée", "Marcha atrás engranada"),

            ["hud.gear.park"] = ("Position parking sélectionnée", "Posición de estacionamiento seleccionada"),
            ["hud.gear.neutral"] = ("Point mort activé", "Punto muerto activo"),
            ["hud.gear.drive"] = ("Marche avant engagée", "Marcha adelante engranada"),
            ["hud.tire.frontleft"] = ("Pneu avant gauche", "Neumático delantero izquierdo"),
            ["hud.tire.frontright"] = ("Pneu avant droit", "Neumático delantero derecho"),
            ["hud.tire.rearleft"] = ("Pneu arrière gauche", "Neumático trasero izquierdo"),
            ["hud.tire.rearright"] = ("Pneu arrière droit", "Neumático trasero derecho"),
            ["hud.media.play"] = ("Reprendre la lecture", "Reanudar la reproducción"),
            ["hud.media.pause"] = ("Mettre la lecture audio en pause", "Pausar la reproducción de audio"),
            ["hud.media.next"] = ("Passer à la piste suivante", "Pasar a la pista siguiente"),
            ["hud.media.volume"] = ("Régler le volume", "Ajustar el volumen"),
            ["hud.climate.fanspeed"] = ("Réglage de la vitesse de ventilation", "Ajuste de la velocidad del ventilador"),
            ["hud.climate.autoclimate"] = ("Climatisation automatique", "Climatizador automático"),
            ["hud.settings.brightness"] = ("Luminosité de l'écran", "Brillo de la pantalla"),
            ["hud.settings.language"] = ("Sélectionner la langue du système", "Seleccionar el idioma del sistema"),
            ["hud.nav.recalculating"] = ("Recalcul de l'itinéraire en cours", "Recalculando la ruta"),
            ["hud.nav.arrived"] = ("Vous arrivez à destination", "Está llegando a su destino"),
            ["hud.battery.low"] = ("Niveau de batterie faible", "Nivel de batería bajo"),
            ["hud.battery.fastcharge"] = ("Recharge rapide en cours", "Carga rápida activa"),

            ["hud.warning.enginetemp"] = (
                "Température du liquide de refroidissement élevée. Réduisez votre vitesse et arrêtez le véhicule en toute sécurité dès que possible.",
                "Temperatura del refrigerante del motor elevada. Reduzca la velocidad y detenga el vehículo de forma segura en cuanto sea posible."),
            ["hud.warning.tirepressure"] = (
                "Pression insuffisante détectée sur le pneu arrière gauche. Veuillez le contrôler et le regonfler rapidement.",
                "Presión baja detectada en el neumático trasero izquierdo. Revíselo e ínflelo cuanto antes."),
            ["hud.assist.lanedeparture"] = (
                "Alerte de franchissement de ligne : dérive involontaire détectée. Gardez les deux mains fermement sur le volant.",
                "Alerta de salida de carril: desvío involuntario detectado. Mantenga ambas manos firmemente en el volante."),
            ["hud.assist.forwardcollision"] = (
                "Alerte de collision frontale : obstacle détecté droit devant. Freinez d'urgence immédiatement.",
                "Aviso de colisión frontal: obstáculo detectado justo delante. Frene de emergencia inmediatamente."),
            ["hud.assist.blindspot"] = (
                "Alerte d'angle mort : véhicule détecté dans la zone adjacente. Ne changez pas de voie.",
                "Alerta de ángulo muerto: vehículo detectado en la zona contigua. No cambie de carril."),
            ["hud.sensor.parkingrear"] = (
                "Capteurs de stationnement arrière à ultrasons actifs. Obstacle détecté à moins d'un mètre du pare-chocs arrière.",
                "Sensores de aparcamiento traseros por ultrasonidos activos. Obstáculo detectado a menos de un metro del parachoques trasero."),
            ["hud.connect.bluetooth"] = (
                "Smartphone du conducteur appairé en Bluetooth. Diffusion audio et appels mains libres disponibles.",
                "Teléfono del conductor emparejado por Bluetooth. Reproducción de audio y llamadas manos libres disponibles."),
            ["hud.nav.tollroad"] = (
                "Péage dans trois kilomètres. Placez-vous dans la voie de télépéage ouverte.",
                "Peaje a tres kilómetros. Sitúese en el carril de telepeaje abierto."),
            ["hud.system.otaavailable"] = (
                "Une mise à jour du logiciel système est prête à être installée. Garez le véhicule et connectez-vous au Wi-Fi.",
                "Hay una actualización del software del sistema lista para instalar. Estacione el vehículo y conéctese a la red Wi-Fi."),
            ["hud.service.oilchange"] = (
                "Vidange de l'huile moteur et remplacement du filtre recommandés dans les huit cents prochains kilomètres.",
                "Se recomienda cambiar el aceite del motor y el filtro en los próximos ochocientos kilómetros."),
            ["hud.service.brakewear"] = (
                "Limite d'usure des plaquettes de frein avant atteinte. Prenez rapidement rendez-vous chez un concessionnaire agréé.",
                "Límite de desgaste de las pastillas de freno delanteras alcanzado. Solicite cuanto antes una revisión en un concesionario autorizado."),
            ["hud.assist.adaptivecruise"] = (
                "Régulateur de vitesse adaptatif activé. Distance de suivi réglée sur trois longueurs de véhicule.",
                "Control de crucero adaptativo activado. Distancia de seguimiento ajustada a tres longitudes de vehículo."),
            ["hud.alert.tractioncontrol"] = (
                "Antipatinage électronique activé. Chaussée glissante détectée sur la route actuelle.",
                "Control de tracción electrónico activado. Se ha detectado calzada deslizante en la vía actual."),
            ["hud.alert.washerfluid"] = (
                "Niveau de liquide lave-glace bas. Veuillez faire l'appoint avec le liquide recommandé.",
                "Nivel bajo de líquido limpiaparabrisas. Rellene el depósito con el líquido recomendado."),

            ["hud.legal.assistdisclaimer"] = (
                "Les systèmes d'aide à la conduite, notamment le régulateur de vitesse adaptatif, le centrage dans la voie et l'atténuation des collisions frontales, sont des équipements de confort complémentaires conçus pour favoriser une conduite sûre. Ces fonctions automatisées ne remplacent ni un conducteur attentif ni un jugement avisé. Vous devez garder les deux mains sur le volant, surveiller en permanence la circulation environnante et rester prêt à reprendre le contrôle manuel du véhicule à tout moment. Les intempéries, un fort éblouissement, un marquage au sol dégradé et l'encrassement des capteurs peuvent réduire la fiabilité du système. Le conducteur demeure pleinement responsable de la sécurité de la conduite et du respect de l'ensemble de la réglementation routière.",
                "Los sistemas de asistencia a la conducción, entre ellos el control de crucero adaptativo, el centrado de carril y la mitigación de colisiones frontales, son funciones complementarias diseñadas para favorecer una conducción segura. Estas funciones automatizadas no sustituyen a un conductor atento ni a un criterio prudente. Debe mantener ambas manos en el volante, vigilar continuamente el tráfico circundante y estar preparado para retomar el control manual del vehículo en cualquier momento. La meteorología adversa, los deslumbramientos intensos, las marcas viales deterioradas y la suciedad en los sensores pueden reducir la fiabilidad del sistema. El conductor sigue siendo plenamente responsable de la conducción segura y del cumplimiento de todas las normas de tráfico."),
            ["hud.legal.dataprivacy"] = (
                "Les services du véhicule connecté collectent et transmettent en temps réel des données de télémétrie, notamment la position géographique précise, les diagnostics de fonctionnement, la durée des trajets et les indicateurs de conduite, vers des serveurs cloud sécurisés. Ces informations servent uniquement à améliorer la précision de la navigation, à assurer le diagnostic à distance, à faciliter l'intervention d'urgence sur route et à perfectionner les systèmes de sécurité. Vous pouvez à tout moment gérer vos préférences de transmission, demander l'export de vos données ou révoquer les autorisations d'analyse cloud dans le menu des paramètres de confidentialité. Des diagnostics techniques anonymes peuvent continuer d'être collectés pour satisfaire aux obligations légales, à la gestion de la garantie et aux rappels obligatoires.",
                "Los servicios del vehículo conectado recopilan y transmiten datos de telemetría en tiempo real, entre ellos la ubicación geográfica precisa, los diagnósticos de funcionamiento, la duración de los trayectos y los indicadores de conducción, a servidores seguros en la nube. Esta información se utiliza únicamente para mejorar la precisión de la navegación, ofrecer diagnóstico remoto, facilitar la asistencia de emergencia en carretera y perfeccionar los sistemas de seguridad. Puede gestionar sus preferencias de transmisión, solicitar la exportación de sus datos o revocar los permisos de análisis en la nube en cualquier momento desde el menú de ajustes de privacidad. Es posible que se sigan recopilando diagnósticos técnicos anónimos para cumplir las obligaciones legales, la gestión de la garantía y las campañas de revisión obligatorias."),
            ["hud.legal.appstoreterms"] = (
                "L'accès aux applications tierces téléchargeables via la boutique numérique embarquée Auroraline et leur utilisation sont régis par les présentes Conditions d'utilisation et par les contrats de licence de chaque développeur. Certaines applications peuvent nécessiter un abonnement actif, une connexion de données cellulaires supplémentaire ou l'appairage d'un appareil mobile pour fonctionner correctement. Les applications ne doivent jamais être utilisées en conduisant si elles distraient le conducteur ou créent un danger. Auroraline décline toute responsabilité en cas d'erreurs de logiciels externes, de paiements intégrés non autorisés, d'indisponibilité de contenus tiers ou d'interruptions de service dues à des pannes des réseaux de télécommunication.",
                "El acceso a las aplicaciones descargables de terceros a través de la tienda digital a bordo de Auroraline, así como su uso, se rigen por las presentes Condiciones de uso y por los acuerdos de licencia de cada desarrollador. Algunas aplicaciones pueden requerir una suscripción activa, una conexión de datos móviles adicional o la vinculación de un dispositivo móvil para funcionar correctamente. Las aplicaciones no deben utilizarse nunca durante la conducción si distraen al conductor o generan un riesgo para la seguridad. Auroraline no asume responsabilidad alguna por errores de software externo, pagos no autorizados dentro de las aplicaciones, la disponibilidad de contenidos de terceros ni las interrupciones del servicio debidas a fallos de las redes de telecomunicaciones."),
            ["hud.legal.otaconsent"] = (
                "Les mises à jour logicielles à distance apportent des améliorations essentielles au véhicule, des évolutions du système d'exploitation, des correctifs de sécurité et des ajustements de conformité réglementaire. Pendant l'installation, le véhicule doit être stationné en lieu sûr, la transmission en position parking et le moteur entièrement coupé. Certains systèmes électroniques critiques pour la sécurité et certaines fonctions de conduite peuvent être temporairement désactivés pendant l'application des mises à jour. N'utilisez pas le véhicule tant que la barre de progression n'est pas terminée et que l'écran d'infodivertissement n'indique pas la réussite de l'opération. Le défaut d'installation en temps utile des mises à jour obligatoires du micrologiciel peut affecter la garantie et le fonctionnement du véhicule.",
                "Las actualizaciones de software inalámbricas aportan mejoras esenciales al vehículo, nuevas versiones del sistema operativo, parches de seguridad y ajustes de cumplimiento normativo. Durante la instalación, el vehículo debe estar estacionado en un lugar seguro, con la transmisión en posición de estacionamiento y el motor completamente apagado. Algunos sistemas electrónicos críticos para la seguridad y ciertas funciones de conducción pueden quedar desactivados temporalmente mientras se aplican las actualizaciones. No utilice el vehículo hasta que la barra de progreso haya finalizado y la pantalla de infoentretenimiento indique que la instalación se ha completado correctamente. No instalar a tiempo las actualizaciones obligatorias del firmware puede afectar a la cobertura de la garantía y al funcionamiento del vehículo."),
            ["hud.legal.sosfeature"] = (
                "La fonction d'assistance d'urgence automatique SOS lance automatiquement un appel vocal mains libres vers les services de secours dès que les capteurs de choc du véhicule enregistrent une collision grave ou le déclenchement d'un airbag. Si les occupants ne peuvent pas répondre, la position du véhicule, sa direction et les données de gravité de l'impact sont automatiquement transmises aux premiers secours. Vous pouvez aussi lancer manuellement un appel d'urgence en maintenant le bouton SOS du plafonnier enfoncé pendant trois secondes. Les services de secours dépendent de la couverture du réseau mobile et de la réception satellite GPS dans la zone où vous vous trouvez.",
                "La función de asistencia de emergencia automática SOS inicia automáticamente una llamada de voz manos libres a los servicios de emergencia cuando los sensores de impacto del vehículo registran una colisión grave o el despliegue de un airbag. Si los ocupantes no pueden responder, las coordenadas del vehículo, el sentido de la marcha y los datos de gravedad del impacto se transmiten automáticamente a los equipos de emergencia. También puede iniciar manualmente una llamada de emergencia manteniendo pulsado el botón SOS del techo durante tres segundos. Los servicios de emergencia dependen de la cobertura de la red móvil y de la recepción de satélites de posicionamiento en la zona en la que se encuentre."),
            ["hud.legal.teendriver"] = (
                "La configuration Conducteur débutant et Surveillance voiturier permet aux titulaires du compte principal de définir des restrictions de conduite personnalisées, notamment une limitation de la vitesse maximale, un plafond de volume audio et la coupure du son tant que les ceintures ne sont pas bouclées. Une fois activé, le système enregistre une télémétrie de conduite complète : freinages brusques, alertes de collision frontale, épisodes de vitesse élevée et interventions du contrôle de stabilité. Un bilan de conduite détaillé est généré et consultable dans l'application mobile connectée après chaque trajet. Ces fonctions de surveillance encouragent une conduite sûre et disciplinée et renforcent les bonnes habitudes des conducteurs secondaires récemment titulaires du permis.",
                "La configuración Conductor novel y Supervisión de aparcacoches permite a los titulares de la cuenta principal establecer restricciones de conducción personalizadas, entre ellas un limitador de velocidad máxima, un tope de volumen de audio y el silenciado del sonido hasta que se abrochen los cinturones. Una vez activado, el sistema registra una telemetría de conducción completa: frenadas bruscas, alertas de colisión frontal, episodios de velocidad elevada e intervenciones del control de estabilidad. Tras cada trayecto se genera un informe de conducción detallado, disponible en la aplicación móvil conectada. Estas funciones de supervisión fomentan una conducción segura y disciplinada y refuerzan los hábitos responsables de los conductores secundarios con el permiso recién obtenido."),
            ["hud.legal.roadsideassist"] = (
                "L'assistance routière Auroraline 24 h/24 et 7 j/7 fournit une aide d'urgence rapide et professionnelle en cas de crevaison, de panne mécanique imprévue, de décharge de la batterie haute tension, de verrouillage des portes et de remorquage d'urgence. Lorsque vous en faites la demande depuis l'affichage tête haute ou l'application pour smartphone, vos coordonnées GPS exactes, le numéro d'identification du véhicule et les diagnostics système en cours sont automatiquement transmis au prestataire d'assistance agréé le plus proche. La disponibilité du service, les distances de remorquage prises en charge et les remboursements varient selon les conditions de garantie du véhicule et le niveau d'adhésion en vigueur. Les services d'assistance routière sont soumis à la réglementation locale de sécurité routière, aux restrictions liées aux intempéries et à la disponibilité des prestataires régionaux.",
                "La asistencia en carretera Auroraline 24/7 ofrece ayuda de emergencia rápida y profesional en caso de pinchazo, avería mecánica imprevista, descarga de la batería de alta tensión, bloqueo de puertas y remolque de emergencia. Cuando la solicita desde la pantalla de visualización frontal o desde la aplicación para teléfono, sus coordenadas GPS exactas, el número de identificación del vehículo y los diagnósticos actuales del sistema se envían automáticamente al proveedor de asistencia autorizado más cercano. La disponibilidad del servicio, los kilómetros de remolque incluidos y la cobertura de reembolso varían según las condiciones de la garantía del vehículo y el nivel de suscripción vigente. Los servicios de asistencia en carretera están sujetos a la normativa local de seguridad vial, a las restricciones por meteorología adversa y a la disponibilidad de los proveedores regionales."),
            ["hud.legal.telemetrydisclosure"] = (
                "Ce véhicule enregistre en continu les codes de défaut, les températures des composants, l'historique des pressions de freinage, les cycles de charge de la batterie et les indicateurs de rendement du groupe motopropulseur. Les enregistrements de télémétrie sont conservés dans des calculateurs embarqués à mémoire non volatile et synchronisés par intermittence avec les bases de données de suivi technique lors des passages en atelier et des sessions sans fil sécurisées. Les données de diagnostic collectées sont utilisées par les techniciens de maintenance et les ingénieurs de développement pour analyser les défaillances imprévues, concevoir des évolutions matérielles plus robustes et affiner les algorithmes embarqués de gestion de l'énergie. Aucun enregistrement vocal biométrique ni aucune image des passagers ne sont captés ou conservés dans le cadre des jeux de données de télémétrie technique standard.",
                "Este vehículo registra de forma continua los códigos de avería, las temperaturas de los componentes, el historial de presiones de frenado, los ciclos de carga de la batería y los indicadores de eficiencia del sistema de propulsión. Los registros de telemetría se almacenan en unidades de control electrónico de a bordo con memoria no volátil y se sincronizan de forma intermitente con las bases de datos de seguimiento técnico durante las visitas al taller y las sesiones inalámbricas seguras. Los datos de diagnóstico recopilados son utilizados por los técnicos de servicio y los ingenieros de desarrollo para investigar fallos imprevistos, diseñar revisiones de hardware más robustas y perfeccionar los algoritmos de gestión de energía de a bordo. En ningún caso se captan ni se conservan grabaciones de voz biométricas ni imágenes de los pasajeros como parte de los conjuntos de datos de telemetría técnica estándar.")
        };
}
