<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" exclude-result-prefixes="msxsl" xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xsl:output method="xml" indent="yes" />
    <xsl:param name="root" />
    <xsl:param name="codee-root" />
    <xsl:include href="../CommonXsltTemplates.xslt"/>
    <xsl:param name="exclude-collections" select="'false'" />
    <xsl:param name="relationship-suffix" select="''" />
    <xsl:variable name="airtable" select="/" />
    <xsl:variable name="squot">'</xsl:variable>
    <xsl:variable name="init-space">             </xsl:variable>
    <xsl:include href="GnfCommon.xslt"/>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <FileSet>

            <FileSetFile>
                    <xsl:element name="RelativePath"><xsl:text>../../../../src/gwbase/types/asl_types.py</xsl:text></xsl:element>

                <OverwriteMode>Always</OverwriteMode>
                <xsl:element name="FileContents">
<xsl:text>""" List of all the types used by the actor."""

from typing import Dict
from typing import List
from typing import no_type_check

from gwbase.types.gw_base import GwBase
</xsl:text>
<xsl:for-each select="$airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase')]">
<xsl:sort select="VersionedTypeName" data-type="text"/>
<xsl:variable name="versioned-type-id" select="VersionedType"/>
<xsl:for-each select="$airtable//VersionedTypes/VersionedType[(VersionedTypeId = $versioned-type-id)  and (Status = 'Active' or Status = 'Pending') and (ProtocolCategory = 'Json' or ProtocolCategory = 'GwAlgoSerial')]">

<xsl:text>
from gwbase.types.</xsl:text>
<xsl:value-of select="translate(TypeName,'.','_')"/>
<xsl:text> import </xsl:text>
<xsl:call-template name="nt-case">
    <xsl:with-param name="type-name-text" select="TypeName" />
</xsl:call-template>
</xsl:for-each>
</xsl:for-each>
<xsl:text>


TypeByName: Dict[str, GwBase] = {}


@no_type_check
def type_makers() -> List[GwBase]:
    return [
        </xsl:text>
<xsl:for-each select="$airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase') and (normalize-space(VersionedTypeName)!='')]">
<xsl:sort select="VersionedTypeName" data-type="text"/>
<xsl:variable name="versioned-type-id" select="VersionedType"/>
<xsl:for-each select="$airtable//VersionedTypes/VersionedType[(VersionedTypeId = $versioned-type-id)  and (Status = 'Active' or Status = 'Pending')  and (ProtocolCategory = 'Json' or ProtocolCategory = 'GwAlgoSerial')]">
<xsl:call-template name="nt-case">
    <xsl:with-param name="type-name-text" select="TypeName" />
</xsl:call-template>
</xsl:for-each>


<xsl:choose>
 <xsl:when test="position() != count($airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase')])">
<xsl:text>,
        </xsl:text>
</xsl:when>
<xsl:otherwise>
<xsl:text>,
    </xsl:text>
</xsl:otherwise>
</xsl:choose>
</xsl:for-each>
    <xsl:text>]


for maker in type_makers():
    TypeByName[maker.type_name_value()] = maker


def version_by_type_name() -> Dict[str, str]:
    """
    Returns:
        Dict[str, str]: Keys are TypeNames, values are versions
    """

    v: Dict[str, str] = {
        </xsl:text>
    <xsl:for-each select="$airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase')]">
    <xsl:sort select="VersionedTypeName" data-type="text"/>
    <xsl:variable name="versioned-type-id" select="VersionedType"/>
    <xsl:for-each select="$airtable//VersionedTypes/VersionedType[(VersionedTypeId = $versioned-type-id)  and (Status = 'Active' or Status = 'Pending') and (ProtocolCategory = 'Json' or ProtocolCategory = 'GwAlgoSerial')]">

    <xsl:text>"</xsl:text>
    <xsl:value-of select="TypeName"/>
    <xsl:text>": "</xsl:text>
    <xsl:value-of select="Version"/>
    <xsl:text>"</xsl:text>
    </xsl:for-each>
    <xsl:choose>
 <xsl:when test="position() != count($airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase')])">
    <xsl:text>,
        </xsl:text>
    </xsl:when>
    <xsl:otherwise>
    <xsl:text>,
    </xsl:text>
    </xsl:otherwise>
    </xsl:choose>
    </xsl:for-each>
    <xsl:text>}

    return v


def status_by_versioned_type_name() -> Dict[str, str]:
    """
    Returns:
        Dict[str, str]: Keys are versioned TypeNames, values are type status
    """

    v: Dict[str, str] = {
        </xsl:text>
    <xsl:for-each select="$airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase')]">
    <xsl:sort select="VersionedTypeName" data-type="text"/>
    <xsl:variable name="versioned-type-id" select="VersionedType"/>
    <xsl:for-each select="$airtable//VersionedTypes/VersionedType[(VersionedTypeId = $versioned-type-id)  and (Status = 'Active' or Status = 'Pending') and (ProtocolCategory = 'Json' or ProtocolCategory = 'GwAlgoSerial')]">
    <xsl:text>"</xsl:text>
    <xsl:value-of select="VersionedTypeName"/>
    <xsl:text>": "</xsl:text>
    <xsl:value-of select="Status"/>
    <xsl:text>"</xsl:text>
    </xsl:for-each>
        <xsl:choose>
 <xsl:when test="position() != count($airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase')])">
    <xsl:text>,
        </xsl:text>
    </xsl:when>
    <xsl:otherwise>
    <xsl:text>,
    </xsl:text>
    </xsl:otherwise>
    </xsl:choose>
    </xsl:for-each>
    <xsl:text>}

    return v
</xsl:text>



                </xsl:element>
            </FileSetFile>


        </FileSet>
    </xsl:template>


</xsl:stylesheet>
